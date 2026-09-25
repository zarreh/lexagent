"""Typed row models for the run store."""

from __future__ import annotations

from dataclasses import dataclass


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


@dataclass(frozen=True)
class RunEvent:
    sequence: int
    node: str
    payload_json: str
