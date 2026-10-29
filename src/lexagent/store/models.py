"""Typed row models for the run store."""

from __future__ import annotations

from dataclasses import dataclass

from zarreh_agentkit.runs import RunEvent


@dataclass(frozen=True)
class RunRecord:
    id: str
    question: str
    status: str  # "running" | "completed" | "failed"
    created_at: str
    updated_at: str
    outcome_kind: str | None  # "answer" | "refusal" | "incomplete"
    answer_json: str | None
    error: str | None


__all__ = ["RunEvent", "RunRecord"]
