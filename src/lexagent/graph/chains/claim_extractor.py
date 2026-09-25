"""Decompose a drafted answer into discrete cited claims."""

from __future__ import annotations

from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from lexagent.graph.protocols import ClaimExtractorChain
from lexagent.prompts.loader import load_prompt
from lexagent.schemas.legal import Claim


def build_claim_extractor_chain(model: BaseChatModel) -> ClaimExtractorChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("claim_extractor_v1")),
            (
                "human",
                "Draft answer:\n{draft_answer}\n\nRetrieved source IDs:\n{source_ids}",
            ),
        ]
    )
    return cast(ClaimExtractorChain, prompt | model.with_structured_output(list[Claim]))
