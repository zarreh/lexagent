"""Deterministic refusal / out-of-scope outcome."""

from lexagent.schemas.legal import LegalAnswer
from lexagent.schemas.state import LexAgentState


def refuse_node(state: LexAgentState) -> dict[str, object]:
    """Return a refusal answer when the query is outside scope."""
    reason = state["refusal_reason"] or "This question is outside LexAgent's scope."
    answer = LegalAnswer(
        rights="",
        obligations="",
        reasoning=reason,
        citations=[],
        confidence="low",
        referral_triggered=True,
    )
    return {"answer": answer}
