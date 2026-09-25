"""Structural (Protocol) types for LLM-backed pieces nodes depend on."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from langchain_core.runnables import Runnable

from lexagent.schemas.legal import (
    Claim,
    LegalAnswer,
    ParsedQuery,
)


class ParseQueryChain(Protocol):
    def invoke(self, input: dict[str, str]) -> ParsedQuery: ...


class ValidateRetrievalChain(Protocol):
    def invoke(self, input: dict[str, object]) -> dict[str, object]: ...


class ReasonChain(Protocol):
    def invoke(self, input: dict[str, object]) -> LegalAnswer: ...


class ClaimExtractorChain(Protocol):
    def invoke(self, input: dict[str, object]) -> Sequence[Claim]: ...


class CitationVerifierChain(Protocol):
    def invoke(self, input: dict[str, object]) -> Sequence[dict[str, object]]: ...


# A looser runtime-compatible alias for nodes that accept any Runnable.
RunnableChain = Runnable[Any, Any]
