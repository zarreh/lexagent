"""Deterministic final assembly of the answer."""

from lexagent.schemas.legal import LegalAnswer
from lexagent.schemas.state import LexAgentState


def publish_node(state: LexAgentState) -> dict[str, object]:
    """Ensure the final answer carries the disclaimer and referral flag."""
    answer = state["answer"]
    if answer is None:
        answer = LegalAnswer(
            rights="",
            obligations="",
            reasoning="No answer was produced.",
            citations=[],
            confidence="low",
            referral_triggered=True,
        )
    return {"answer": answer}
