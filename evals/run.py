"""Canonical evaluation harness for LexAgent.

Layer 1: retrieval recall against canonical and paraphrased scenarios. The keyword
store needs no key; the semantic Qdrant store is added when Qdrant and an OpenAI
key are available. Future layers will evaluate the full graph via LLM-as-judge.
"""

from __future__ import annotations

from evals.metrics import evaluate_retrieval, print_report
from evals.scenarios import CANONICAL_SCENARIOS, PARAPHRASE_SCENARIOS
from lexagent.retrieval.store import CorpusStore, LocalCorpusStore, build_store
from lexagent.settings import get_settings


def _run(name: str, store: CorpusStore) -> None:
    for label, scenarios in (
        ("canonical", CANONICAL_SCENARIOS),
        ("paraphrase", PARAPHRASE_SCENARIOS),
    ):
        print(f"\n== {name} store / {label} ==")
        print_report(evaluate_retrieval(store, top_k=4, scenarios=scenarios))


def main() -> None:
    _run("keyword", LocalCorpusStore())
    store = build_store(get_settings())
    if not isinstance(store, LocalCorpusStore):
        _run("semantic", store)
    else:
        print("\n(semantic store skipped: Qdrant or OpenAI key unavailable)")


if __name__ == "__main__":
    main()
