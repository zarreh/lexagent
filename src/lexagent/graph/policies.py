"""Model selection per node — never inline in a node."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from lexagent.settings import Settings

FAST_MODEL = "gpt-4o-mini"
REASONING_MODEL = "gpt-4o"


def _api_key(settings: Settings) -> SecretStr | None:
    return SecretStr(settings.openai_api_key) if settings.openai_api_key else None


def build_fast_model(settings: Settings) -> ChatOpenAI:
    """Parse, validate, extract claims — cheap, structured output."""
    return ChatOpenAI(model=FAST_MODEL, temperature=0, api_key=_api_key(settings))


def build_reasoning_model(settings: Settings) -> ChatOpenAI:
    """Reason and verify citations — the judgement the answer is graded on."""
    return ChatOpenAI(model=REASONING_MODEL, temperature=0, api_key=_api_key(settings))
