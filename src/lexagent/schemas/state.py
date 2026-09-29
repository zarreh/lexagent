from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from lexagent.schemas.legal import (
    CitationReport,
    LegalAnswer,
    ParsedQuery,
    RetrievedSource,
)


class SkeletonState(TypedDict):
    """Phase 0 walking-skeleton state — kept as the template's trivial proof graph."""

    message: str
    echoed: str
    done: bool


class LexAgentState(TypedDict):
    """Full reasoning-graph state for LexAgent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    question: str
    parsed_query: ParsedQuery | None
    retrieved_sources: Annotated[list[RetrievedSource], lambda a, b: a + b]
    retrieval_attempts: int
    verification_attempts: int
    draft_answer: str
    claims: list[dict[str, object]]
    citation_report: CitationReport | None
    answer: LegalAnswer | None
    refusal_reason: str | None
    started_at: float
