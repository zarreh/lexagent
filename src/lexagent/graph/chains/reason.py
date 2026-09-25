"""Draft a legal answer from retrieved sources."""

from __future__ import annotations

from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from lexagent.graph.protocols import ReasonChain
from lexagent.prompts.loader import load_prompt
from lexagent.schemas.legal import LegalAnswer


def build_reason_chain(model: BaseChatModel) -> ReasonChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("reason_v1")),
            (
                "human",
                "Question: {question}\n\nJurisdiction: {jurisdiction}\n\nSources:\n{sources}",
            ),
        ]
    )
    return cast(ReasonChain, prompt | model.with_structured_output(LegalAnswer))
