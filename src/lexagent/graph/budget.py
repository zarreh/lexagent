"""Per-run cost guardrail for LexAgent (docs/PLAN.md §5.5)."""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.messages import BaseMessage
from zarreh_agentkit.guardrails.budget import (
    Budget,
    count_tool_calls,
)
from zarreh_agentkit.guardrails.budget import (
    budget_breach_reason as _budget_breach_reason,
)

DEFAULT_BUDGET = Budget()

__all__ = ["Budget", "DEFAULT_BUDGET", "budget_breach_reason", "count_tool_calls"]


def budget_breach_reason(
    messages: Sequence[BaseMessage], started_at: float, budget: Budget = DEFAULT_BUDGET
) -> str | None:
    """Returns a human-readable breach reason, or None if within budget."""
    return _budget_breach_reason(count_tool_calls(messages), started_at, budget)
