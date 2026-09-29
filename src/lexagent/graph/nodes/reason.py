"""Draft a structured legal answer from retrieved sources."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from lexagent.graph.protocols import ReasonChain
from lexagent.schemas.state import LexAgentState


def build_reason_node(
    chain: ReasonChain,
) -> Callable[[LexAgentState], Awaitable[dict[str, object]]]:
    async def reason_node(state: LexAgentState) -> dict[str, object]:
        parsed = state["parsed_query"]
        jurisdiction = parsed.jurisdiction if parsed is not None else "unknown"
        sources = state["retrieved_sources"]
        answer = await chain.ainvoke(
            {
                "question": state["question"],
                "jurisdiction": jurisdiction,
                "sources": [s.model_dump() for s in sources],
            }
        )
        return {
            "answer": answer,
            "draft_answer": answer.reasoning,
        }

    return reason_node
