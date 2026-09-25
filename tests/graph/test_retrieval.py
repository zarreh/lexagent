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
