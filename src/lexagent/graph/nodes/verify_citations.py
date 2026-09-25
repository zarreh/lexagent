"""Verify citations and aggregate unsupported count deterministically."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from langchain_core.messages import HumanMessage

from lexagent.graph.protocols import CitationVerifierChain
from lexagent.schemas.legal import CitationReport, ClaimJudgment
from lexagent.schemas.state import LexAgentState


def _confidence_for(unsupported: int) -> Literal["high", "medium", "low"]:
    if unsupported == 0:
        return "high"
    if unsupported == 1:
        return "medium"
    return "low"


def _feedback_text(judgments: list[ClaimJudgment]) -> str:
    lines = [f'- "{j.claim_id}" — {j.reason}' for j in judgments if not j.supported]
    header = (
        "The following claims are not supported by the retrieved sources. "
        "Revise the answer to either substantiate or remove them:"
    )
    return header + "\n" + "\n".join(lines)


def build_verify_citations_node(
    chain: CitationVerifierChain,
) -> Callable[[LexAgentState], dict[str, object]]:
    def verify_citations_node(state: LexAgentState) -> dict[str, object]:
        raw = chain.invoke(
            {
                "claims": state["claims"],
                "sources": [s.model_dump() for s in state["retrieved_sources"]],
            }
        )
        judgments = [ClaimJudgment(**r) for r in raw]  # type: ignore[arg-type]
        unsupported = sum(1 for j in judgments if not j.supported)
        report = CitationReport(
            claims=judgments,
            unsupported=unsupported,
            confidence=_confidence_for(unsupported),
        )
        delta: dict[str, object] = {"citation_report": report}
        if unsupported > 0:
            delta["messages"] = [HumanMessage(content=_feedback_text(judgments))]
        return delta

    return verify_citations_node
