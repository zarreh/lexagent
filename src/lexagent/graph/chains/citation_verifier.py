"""Verify that each claim's citations are supported by the retrieved sources."""

from __future__ import annotations

from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from lexagent.graph.protocols import CitationVerifierChain
from lexagent.prompts.loader import load_prompt
from lexagent.schemas.legal import ClaimJudgment


def build_citation_verifier_chain(model: BaseChatModel) -> CitationVerifierChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("citation_verifier_v1")),
            (
                "human",
                "Claims:\n{claims}\n\nRetrieved sources:\n{sources}",
            ),
        ]
    )
    return cast(
        CitationVerifierChain,
        prompt | model.with_structured_output(list[ClaimJudgment]),
    )
