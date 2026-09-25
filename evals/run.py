"""Canonical evaluation harness for LexAgent.

Layer 1: retrieval recall against the canonical scenario set. This needs no
LLM API key. Future layers will evaluate the full reasoning graph via LLM-as-judge.
"""

from __future__ import annotations

from evals.metrics import evaluate_retrieval, print_report
from lexagent.retrieval.store import LocalCorpusStore


def main() -> None:
    store = LocalCorpusStore()
    report = evaluate_retrieval(store, top_k=4)
    print_report(report)


if __name__ == "__main__":
    main()
