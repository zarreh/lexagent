"""Domain schemas for LexAgent's legal reasoning graph."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ParsedQuery(BaseModel):
    """Structured output of the query parser node."""

    intent: str
    jurisdiction: Literal["TX", "CA", "unknown"] = "unknown"
    issue_type: str
    missing_info: list[str] = Field(default_factory=list)
    in_scope: bool = True


class RetrievedSource(BaseModel):
    """One retrieved statute or precedent chunk."""

    source_id: str
    corpus: Literal["statute", "precedent"]
    jurisdiction: Literal["TX", "CA"]
    title: str
    text: str


class Citation(BaseModel):
    """A single citation inside a claim."""

    source_id: str
    corpus: Literal["statute", "precedent"]
    quoted_span: str | None = None


class Claim(BaseModel):
    """One atomic claim extracted from the drafted answer."""

    id: str
    text: str
    citations: list[Citation] = Field(default_factory=list)


class ClaimJudgment(BaseModel):
    """Per-claim verification result."""

    claim_id: str
    supported: bool
    reason: str


class CitationReport(BaseModel):
    """Aggregated citation-verification output."""

    claims: list[ClaimJudgment]
    unsupported: int
    confidence: Literal["high", "medium", "low"]


class LegalAnswer(BaseModel):
    """Final structured answer returned to the user."""

    rights: str
    obligations: str
    reasoning: str
    citations: list[Citation]
    confidence: Literal["high", "medium", "low"]
    referral_triggered: bool
    disclaimer: str = (
        "This is research-oriented information, not legal advice. "
        "Consult a licensed attorney for advice on your specific situation."
    )
