"""Extract discrete cited claims from the drafted answer."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from lexagent.graph.protocols import ClaimExtractorChain
from lexagent.schemas.state import LexAgentState


def build_extract_claims_node(
    chain: ClaimExtractorChain,
) -> Callable[[LexAgentState], Awaitable[dict[str, object]]]:
    async def extract_claims_node(state: LexAgentState) -> dict[str, object]:
        source_ids = [s.source_id for s in state["retrieved_sources"]]
        wrapper = await chain.ainvoke(
            {
                "draft_answer": state["draft_answer"],
                "source_ids": source_ids,
            }
        )
        return {"claims": [c.model_dump() for c in wrapper.claims]}

    return extract_claims_node
