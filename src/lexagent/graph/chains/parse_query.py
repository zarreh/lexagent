"""Parse a free-form legal question into a structured query."""

from __future__ import annotations

from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from lexagent.graph.protocols import ParseQueryChain
from lexagent.prompts.loader import load_prompt
from lexagent.schemas.legal import ParsedQuery


def build_parse_query_chain(model: BaseChatModel) -> ParseQueryChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("parse_query_v1")),
            ("human", "Question:\n{question}"),
        ]
    )
    # BaseChatModel.with_structured_output returns a Runnable whose invoke
    # signature is broader than the narrow Protocol; cast is safe because the
    # chain is always invoked with the declared input shape.
    return cast(ParseQueryChain, prompt | model.with_structured_output(ParsedQuery))
