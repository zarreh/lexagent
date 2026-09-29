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
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Protocol

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from lexagent.schemas.legal import RetrievedSource


class CorpusStore(Protocol):
    """Abstract corpus store: search returns ranked retrieved sources."""

    def search(
        self, query: str, jurisdiction: str, corpus: str, top_k: int = 4
    ) -> list[RetrievedSource]: ...


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
        query_terms = set(query.lower().split())
        text_terms = set(text.lower().split())
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
            score = self._score(query, f"{title} {text} {facts} {holding}")
            if score > 0:
                scored.append((score, record))
        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[RetrievedSource] = []
        for _, record in scored[:top_k]:
            text = record.get("text", "")
            juris_val = record.get("jurisdiction", jurisdiction)
            if juris_val not in ("TX", "CA"):
                continue
            juris_lit: Literal["TX", "CA"] = juris_val  # type: ignore[assignment]
            corpus_lit: Literal["statute", "precedent"] = (
                "statute" if corpus == "statute" else "precedent"
            )
            display_text = text if text else f"{facts}\n\n{holding}"
            results.append(
                RetrievedSource(
                    source_id=record.get("id") or record.get("case_id", ""),
                    corpus=corpus_lit,
                    jurisdiction=juris_lit,
                    title=record.get("title", ""),
                    text=display_text,
                )
            )
        return results


class QdrantCorpusStore:
    """Semantic search over Qdrant collections."""

    def __init__(
        self,
        client: QdrantClient,
        embeddings: OpenAIEmbeddings,
        statute_collection: str,
        precedent_collection: str,
    ) -> None:
        self._statute_store = QdrantVectorStore(
            client=client,
            collection_name=statute_collection,
            embedding=embeddings,
        )
        self._precedent_store = QdrantVectorStore(
            client=client,
            collection_name=precedent_collection,
            embedding=embeddings,
        )

    def _to_sources(self, docs: Sequence[object], corpus: str) -> list[RetrievedSource]:
        results: list[RetrievedSource] = []
        for doc in docs:
            metadata = getattr(doc, "metadata", {})
            text = getattr(doc, "page_content", "")
            juris: str = metadata.get("jurisdiction", "unknown")
            corpus_lit: Literal["statute", "precedent"] = corpus  # type: ignore[assignment]
            juris_lit: Literal["TX", "CA"] = juris if juris in ("TX", "CA") else "TX"  # type: ignore[assignment]
            results.append(
                RetrievedSource(
                    source_id=metadata.get("id") or metadata.get("case_id", ""),
                    corpus=corpus_lit,
                    jurisdiction=juris_lit,
                    title=metadata.get("title", ""),
                    text=text,
                )
            )
        return results

    def search(
        self, query: str, jurisdiction: str, corpus: str, top_k: int = 4
    ) -> list[RetrievedSource]:
        store = self._statute_store if corpus == "statute" else self._precedent_store
        filter_ = None
        if jurisdiction != "unknown":
            from qdrant_client.http.models import FieldCondition, Filter, MatchValue

            filter_ = Filter(
                must=[FieldCondition(key="jurisdiction", match=MatchValue(value=jurisdiction))]
            )
        docs = store.similarity_search(query, k=top_k, filter=filter_)
        return self._to_sources(docs, corpus)
