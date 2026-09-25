"""Build Qdrant vector indexes for statutes and precedents.

Requires an OpenAI API key for embeddings and a running Qdrant instance.
The script is idempotent: it recreates the configured collections.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from data.seed_precedents import PrecedentSummary, all_precedents
from data.seed_statutes import StatuteSection, all_statutes


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEXAGENT_", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "lexagent"
    openai_api_key: str = ""


def _client(settings: _Settings) -> QdrantClient:
    kwargs: dict[str, Any] = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantClient(**kwargs)


def _embeddings(settings: _Settings) -> OpenAIEmbeddings:
    key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required to build embeddings")
    return OpenAIEmbeddings(api_key=key)


def _recreate_collection(client: QdrantClient, name: str) -> None:
    client.recreate_collection(
        collection_name=name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )


def build_statute_index(
    client: QdrantClient, embeddings: OpenAIEmbeddings, collection_name: str
) -> None:
    """Index statute sections into Qdrant."""
    _recreate_collection(client, collection_name)
    sections = all_statutes()
    texts = [s.to_markdown() for s in sections]
    metadatas = [s.model_dump() for s in sections]
    store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    store.add_texts(texts=texts, metadatas=metadatas)


def build_precedent_index(
    client: QdrantClient, embeddings: OpenAIEmbeddings, collection_name: str
) -> None:
    """Index synthetic precedents into Qdrant."""
    _recreate_collection(client, collection_name)
    precedents = all_precedents()
    texts = [p.to_markdown() for p in precedents]
    metadatas = [p.model_dump() for p in precedents]
    store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    store.add_texts(texts=texts, metadatas=metadatas)


def write_sample_index(client: QdrantClient, output_dir: Path) -> None:
    """Persist a tiny JSON snapshot of the collections for inspection."""
    output_dir.mkdir(parents=True, exist_ok=True)
    statutes = [StatuteSection(**d).model_dump() for d in all_statutes()]
    precedents = [PrecedentSummary(**d).model_dump() for d in all_precedents()]
    with (output_dir / "statutes.jsonl").open("w", encoding="utf-8") as f:
        for record in statutes:
            f.write(json.dumps(record) + "\n")
    with (output_dir / "precedents.json").open("w", encoding="utf-8") as f:
        json.dump(precedents, f, indent=2)


def main() -> None:
    settings = _Settings()
    client = _client(settings)
    embeddings = _embeddings(settings)

    statute_collection = f"{settings.qdrant_collection}_statutes"
    precedent_collection = f"{settings.qdrant_collection}_precedents"

    build_statute_index(client, embeddings, statute_collection)
    build_precedent_index(client, embeddings, precedent_collection)

    sample_dir = Path(__file__).with_name("sample")
    write_sample_index(client, sample_dir)

    print(
        f"Indexed statutes into '{statute_collection}' and precedents into '{precedent_collection}'"
    )


if __name__ == "__main__":
    main()
