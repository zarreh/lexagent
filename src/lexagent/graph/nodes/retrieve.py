"""Retrieve statute and precedent sources for the parsed query."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from lexagent.retrieval.store import CorpusStore
from lexagent.schemas.state import LexAgentState


def build_retrieve_node(
    store: CorpusStore,
) -> Callable[[LexAgentState], Awaitable[dict[str, object]]]:
    async def retrieve_node(state: LexAgentState) -> dict[str, object]:
        parsed = state["parsed_query"]
        jurisdiction = parsed.jurisdiction if parsed is not None else "unknown"
        query = state["question"]
        # The parsed issue words bridge lay phrasing ("broken heater") to statute vocabulary.
        enriched = f"{query} {parsed.issue_type} {parsed.intent}" if parsed is not None else query
        statutes = store.search(enriched, jurisdiction, "statute", top_k=4)
        precedents = store.search(enriched, jurisdiction, "precedent", top_k=4)
        return {
            "retrieved_sources": statutes + precedents,
            "retrieval_attempts": state["retrieval_attempts"] + 1,
        }

    return retrieve_node
