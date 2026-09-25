"""Retrieve statute and precedent sources for the parsed query."""

from __future__ import annotations

from collections.abc import Callable

from lexagent.retrieval.store import CorpusStore
from lexagent.schemas.state import LexAgentState


def build_retrieve_node(
    store: CorpusStore,
) -> Callable[[LexAgentState], dict[str, object]]:
    def retrieve_node(state: LexAgentState) -> dict[str, object]:
        parsed = state["parsed_query"]
        jurisdiction = parsed.jurisdiction if parsed is not None else "unknown"
        query = state["question"]
        statutes = store.search(query, jurisdiction, "statute", top_k=4)
        # Precedent summaries use issue words; fall back to the issue_type if the
        # raw question has no keyword overlap with the synthetic holdings.
        precedent_query = f"{query} {parsed.issue_type}" if parsed is not None else query
        precedents = store.search(precedent_query, jurisdiction, "precedent", top_k=4)
        return {
            "retrieved_sources": statutes + precedents,
            "retrieval_attempts": state["retrieval_attempts"] + 1,
        }

    return retrieve_node
