"""Corpus stores for statutes and precedents.

Two implementations are provided:
- `LocalCorpusStore` loads the committed sample files and scores by keyword
  overlap. It requires no network or embedding key, so tests and local demos
  run without Qdrant or OpenAI.
- `QdrantCorpusStore` uses `langchain-qdrant` for semantic search when a
  Qdrant instance is available.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Literal, Protocol

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from pydantic import SecretStr
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, VectorParams

from lexagent.observability import get_logger
from lexagent.schemas.legal import RetrievedSource
from lexagent.settings import Settings

logger = get_logger(__name__)


class CorpusStore(Protocol):
    """Abstract corpus store: search returns ranked retrieved sources."""

    def search(
        self, query: str, jurisdiction: str, corpus: str, top_k: int = 4
    ) -> list[RetrievedSource]: ...


def _record_to_source(record: dict[str, str], corpus: str) -> RetrievedSource | None:
    juris = record.get("jurisdiction", "")
    if juris not in ("TX", "CA"):
        return None
    juris_lit: Literal["TX", "CA"] = juris  # type: ignore[assignment]
    corpus_lit: Literal["statute", "precedent"] = "statute" if corpus == "statute" else "precedent"
    text = record.get("text") or f"{record.get('facts', '')}\n\n{record.get('holding', '')}"
    return RetrievedSource(
        source_id=record.get("id") or record.get("case_id", ""),
        corpus=corpus_lit,
        jurisdiction=juris_lit,
        title=record.get("title") or record.get("issue", ""),
        text=text,
    )


class LocalCorpusStore:
    """Keyword-based local corpus store backed by the committed sample files."""

    def __init__(self, sample_dir: Path | None = None) -> None:
        if sample_dir is None:
            default = Path(__file__).parent.parent.parent.parent / "data" / "sample"
            sample_dir = Path(os.environ.get("LEXAGENT_DATA_DIR", default))
        self._statutes = self._load_statutes(sample_dir / "statutes.jsonl")
        self._precedents = self._load_precedents(sample_dir / "precedents.json")

    def _load_statutes(self, path: Path) -> list[dict[str, str]]:
        records: list[dict[str, str]] = []
        if not path.exists():
            return records
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def _load_precedents(self, path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def _score(self, query: str, text: str) -> int:
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        text_terms = set(re.findall(r"[a-z0-9]+", text.lower()))
        return len(query_terms & text_terms)

    def search(
        self, query: str, jurisdiction: str, corpus: str, top_k: int = 4
    ) -> list[RetrievedSource]:
        records = self._statutes if corpus == "statute" else self._precedents
        scored: list[tuple[int, dict[str, str]]] = []
        for record in records:
            if jurisdiction != "unknown" and record.get("jurisdiction") != jurisdiction:
                continue
            text = record.get("text", "")
            title = record.get("title", "")
            facts = record.get("facts", "")
            holding = record.get("holding", "")
            issue = record.get("issue", "")
            score = self._score(query, f"{title} {issue} {text} {facts} {holding}")
            if score > 0:
                scored.append((score, record))
        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[RetrievedSource] = []
        for _, record in scored[:top_k]:
            source = _record_to_source(record, corpus)
            if source is not None:
                results.append(source)
        return results

    def records(self, corpus: str) -> list[dict[str, str]]:
        return self._statutes if corpus == "statute" else self._precedents


class QdrantCorpusStore:
    """Semantic search over one Qdrant collection per corpus."""

    def __init__(
        self,
        client: QdrantClient,
        embeddings: Embeddings,
        statute_collection: str,
        precedent_collection: str,
    ) -> None:
        self._stores = {
            "statute": QdrantVectorStore(
                client=client, collection_name=statute_collection, embedding=embeddings
            ),
            "precedent": QdrantVectorStore(
                client=client, collection_name=precedent_collection, embedding=embeddings
            ),
        }

    def search(
        self, query: str, jurisdiction: str, corpus: str, top_k: int = 4
    ) -> list[RetrievedSource]:
        filter_ = None
        if jurisdiction != "unknown":
            # langchain-qdrant nests document metadata under the "metadata" payload key.
            filter_ = Filter(
                must=[
                    FieldCondition(
                        key="metadata.jurisdiction", match=MatchValue(value=jurisdiction)
                    )
                ]
            )
        docs = self._stores[corpus if corpus in self._stores else "statute"].similarity_search(
            query, k=top_k, filter=filter_
        )
        sources: list[RetrievedSource] = []
        for doc in docs:
            record = {**doc.metadata, "text": doc.page_content}
            source = _record_to_source(record, corpus)
            if source is not None:
                sources.append(source)
        return sources


def _index_collection(
    client: QdrantClient,
    embeddings: Embeddings,
    name: str,
    records: list[dict[str, str]],
    corpus: str,
) -> None:
    """Create and fill a collection unless it already holds this many points."""
    if client.collection_exists(name) and client.count(name).count == len(records):
        return
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        name,
        vectors_config=VectorParams(
            size=len(embeddings.embed_query("dim")), distance=Distance.COSINE
        ),
    )
    texts: list[str] = []
    metadatas: list[dict[str, str]] = []
    for record in records:
        source = _record_to_source(record, corpus)
        if source is None:
            continue
        texts.append(f"{source.title}\n{source.text}")
        metadatas.append(
            {"id": source.source_id, "jurisdiction": source.jurisdiction, "title": source.title}
        )
    QdrantVectorStore(client=client, collection_name=name, embedding=embeddings).add_texts(
        texts=texts, metadatas=metadatas
    )


def build_store(settings: Settings) -> CorpusStore:
    """Semantic Qdrant store when reachable and embeddable, else the keyword store."""
    local = LocalCorpusStore()
    if not settings.openai_api_key:
        return local
    try:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
            timeout=10,
            check_compatibility=False,
        )
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", api_key=SecretStr(settings.openai_api_key)
        )
        _index_collection(
            client, embeddings, settings.statute_collection, local.records("statute"), "statute"
        )
        _index_collection(
            client,
            embeddings,
            settings.precedent_collection,
            local.records("precedent"),
            "precedent",
        )
        store = QdrantCorpusStore(
            client, embeddings, settings.statute_collection, settings.precedent_collection
        )
    except Exception:  # noqa: BLE001
        logger.warning("qdrant_unavailable_using_keyword_store", exc_info=True)
        return local
    logger.info("using_qdrant_store", url=settings.qdrant_url)
    return store
