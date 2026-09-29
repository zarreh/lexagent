from lexagent.retrieval.store import LocalCorpusStore
from lexagent.schemas.legal import RetrievedSource


def test_local_store_searches_both_corpora() -> None:
    store = LocalCorpusStore()
    statutes = store.search("security deposit refund", "TX", "statute", top_k=2)
    precedents = store.search("security deposit refund", "TX", "precedent", top_k=2)

    assert all(isinstance(s, RetrievedSource) for s in statutes)
    assert all(s.corpus == "statute" for s in statutes)
    assert all(isinstance(p, RetrievedSource) for p in precedents)
    assert all(p.corpus == "precedent" for p in precedents)


def test_local_store_filters_by_jurisdiction() -> None:
    store = LocalCorpusStore()
    tx = store.search("eviction notice", "TX", "statute", top_k=10)
    ca = store.search("eviction notice", "CA", "statute", top_k=10)
    assert all(s.jurisdiction == "TX" for s in tx)
    assert all(s.jurisdiction == "CA" for s in ca)


def test_qdrant_store_indexes_once_and_filters_by_jurisdiction() -> None:
    from langchain_core.embeddings import DeterministicFakeEmbedding
    from qdrant_client import QdrantClient

    from lexagent.retrieval.store import QdrantCorpusStore, _index_collection

    local = LocalCorpusStore()
    client = QdrantClient(":memory:")
    embeddings = DeterministicFakeEmbedding(size=32)
    for corpus, name in (("statute", "s"), ("precedent", "p")):
        _index_collection(client, embeddings, name, local.records(corpus), corpus)
        _index_collection(client, embeddings, name, local.records(corpus), corpus)
        assert client.count(name).count == len(local.records(corpus))

    store = QdrantCorpusStore(client, embeddings, "s", "p")
    statutes = store.search("security deposit refund", "CA", "statute", top_k=5)
    assert statutes
    assert {s.jurisdiction for s in statutes} == {"CA"}
    assert {s.corpus for s in statutes} == {"statute"}
    precedents = store.search("repair", "TX", "precedent", top_k=3)
    assert precedents
    assert all(p.text.strip() and p.source_id.startswith("SYN-") for p in precedents)


def test_build_store_falls_back_to_keyword_store_without_key() -> None:
    from lexagent.retrieval.store import build_store
    from lexagent.settings import Settings

    assert isinstance(build_store(Settings(openai_api_key="")), LocalCorpusStore)


def test_build_store_falls_back_when_qdrant_unreachable() -> None:
    from lexagent.retrieval.store import build_store
    from lexagent.settings import Settings

    settings = Settings(openai_api_key="sk-test", qdrant_url="http://127.0.0.1:1")
    assert isinstance(build_store(settings), LocalCorpusStore)


def test_local_precedents_return_their_own_text() -> None:
    store = LocalCorpusStore()
    results = store.search("security deposit", "TX", "precedent", top_k=4)
    texts = {r.source_id: r.text for r in results}
    assert len(set(texts.values())) == len(texts)
    assert all(r.title for r in results)
