"""Judge whether retrieved sources are relevant enough, or expansion is needed."""

from __future__ import annotations

from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from lexagent.graph.protocols import ValidateRetrievalChain
from lexagent.prompts.loader import load_prompt
from lexagent.schemas.legal import RetrievalValidation


def build_validate_retrieval_chain(model: BaseChatModel) -> ValidateRetrievalChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("validate_retrieval_v1")),
            (
                "human",
                "Question: {question}\n\nRetrieved sources:\n{sources}",
            ),
        ]
    )
    return cast(
        ValidateRetrievalChain,
        prompt | model.with_structured_output(RetrievalValidation),
    )
