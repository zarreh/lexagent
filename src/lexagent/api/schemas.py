"""API-contract request/response models — separate from `schemas/`, which
holds the domain models the graph itself produces.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4096)


class AskResponse(BaseModel):
    id: str
    status: str
