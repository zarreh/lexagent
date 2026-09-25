"""Terminal node when the cost guardrail trips."""

from __future__ import annotations

from lexagent.graph.budget import budget_breach_reason
from lexagent.schemas.legal import LegalAnswer
from lexagent.schemas.state import LexAgentState


def budget_exceeded_node(state: LexAgentState) -> dict[str, object]:
    """Return an incomplete answer rather than silently truncating."""
    reason = budget_breach_reason(state["messages"], state["started_at"]) or "budget exceeded"
    answer = LegalAnswer(
        rights="",
        obligations="",
        reasoning=(
            "LexAgent could not finish within the per-run cost guardrail "
            "and was stopped before reaching a grounded conclusion."
        ),
        citations=[],
        confidence="low",
        referral_triggered=True,
    )
    return {"answer": answer, "refusal_reason": reason}
