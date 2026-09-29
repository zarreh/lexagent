"""Routing predicates for the LexAgent graph."""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage

from lexagent.schemas.state import LexAgentState

MAX_RETRIEVAL_ATTEMPTS = 3
MAX_VERIFICATION_PASSES = 2


def route_after_parse(
    state: LexAgentState,
) -> Literal["retrieve", "refuse"]:
    parsed = state["parsed_query"]
    if parsed is None or not parsed.in_scope:
        return "refuse"
    return "retrieve"


def route_after_validate(
    state: LexAgentState,
) -> Literal["reason", "retrieve"]:
    # If a feedback message was added, retrieval was not relevant.
    if state["messages"] and isinstance(state["messages"][-1], HumanMessage):
        # Feedback is added only on irrelevance; loop back to retrieve.
        return "retrieve" if state["retrieval_attempts"] < MAX_RETRIEVAL_ATTEMPTS else "reason"
    return "reason"


def route_after_verify(
    state: LexAgentState,
) -> Literal["publish", "reason", "budget_exceeded"]:
    report = state["citation_report"]
    if report is None:
        return "reason"
    if report.unsupported == 0:
        return "publish"
    return "reason" if state["verification_attempts"] < MAX_VERIFICATION_PASSES else "publish"
