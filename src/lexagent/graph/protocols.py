"""Structural (Protocol) types for LLM-backed pieces nodes depend on."""

from __future__ import annotations

from typing import Any, Protocol

from langchain_core.runnables import Runnable

from lexagent.schemas.legal import (
    ClaimJudgmentList,
    ClaimList,
    LegalAnswer,
    ParsedQuery,
    RetrievalValidation,
)


class ParseQueryChain(Protocol):
    def invoke(self, input: dict[str, str]) -> ParsedQuery: ...
    async def ainvoke(self, input: dict[str, str]) -> ParsedQuery: ...


class ValidateRetrievalChain(Protocol):
    def invoke(self, input: dict[str, object]) -> RetrievalValidation: ...
    async def ainvoke(self, input: dict[str, object]) -> RetrievalValidation: ...


class ReasonChain(Protocol):
    def invoke(self, input: dict[str, object]) -> LegalAnswer: ...
    async def ainvoke(self, input: dict[str, object]) -> LegalAnswer: ...


class ClaimExtractorChain(Protocol):
    def invoke(self, input: dict[str, object]) -> ClaimList: ...
    async def ainvoke(self, input: dict[str, object]) -> ClaimList: ...


class CitationVerifierChain(Protocol):
    def invoke(self, input: dict[str, object]) -> ClaimJudgmentList: ...
    async def ainvoke(self, input: dict[str, object]) -> ClaimJudgmentList: ...


# A looser runtime-compatible alias for nodes that accept any Runnable.
RunnableChain = Runnable[Any, Any]
