"""Verify citations and aggregate unsupported count deterministically."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from langchain_core.messages import HumanMessage
from zarreh_agentkit.guardrails.grounding import (
    count_unsupported,
    grounding_confidence,
    unsupported_claims_feedback,
)

from lexagent.graph.protocols import CitationVerifierChain
from lexagent.schemas.legal import CitationReport
from lexagent.schemas.state import LexAgentState

_FEEDBACK_HEADER = (
    "The following claims are not supported by the retrieved sources. "
    "Revise the answer to either substantiate or remove them:"
)


def build_verify_citations_node(
    chain: CitationVerifierChain,
) -> Callable[[LexAgentState], Awaitable[dict[str, object]]]:
    async def verify_citations_node(state: LexAgentState) -> dict[str, object]:
        wrapper = await chain.ainvoke(
            {
                "claims": state["claims"],
                "sources": [s.model_dump() for s in state["retrieved_sources"]],
            }
        )
        judgments = wrapper.judgments
        unsupported = count_unsupported(judgments)
        report = CitationReport(
            claims=judgments,
            unsupported=unsupported,
            confidence=grounding_confidence(unsupported),
        )
        delta: dict[str, object] = {
            "citation_report": report,
            "verification_attempts": state["verification_attempts"] + 1,
        }
        if unsupported > 0:
            delta["messages"] = [
                HumanMessage(content=unsupported_claims_feedback(judgments, _FEEDBACK_HEADER))
            ]
        return delta

    return verify_citations_node
