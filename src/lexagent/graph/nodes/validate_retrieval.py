"""Judge whether retrieval returned relevant sources; request expansion if not."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from langchain_core.messages import HumanMessage

from lexagent.graph.protocols import ValidateRetrievalChain
from lexagent.schemas.legal import RetrievalValidation
from lexagent.schemas.state import LexAgentState


def build_validate_retrieval_node(
    chain: ValidateRetrievalChain,
) -> Callable[[LexAgentState], Awaitable[dict[str, object]]]:
    async def validate_retrieval_node(state: LexAgentState) -> dict[str, object]:
        sources = state["retrieved_sources"]
        result = await chain.ainvoke(
            {
                "question": state["question"],
                "sources": [s.model_dump() for s in sources],
            }
        )
        validation = RetrievalValidation.model_validate(result)
        delta: dict[str, object] = {}
        if not validation.relevant:
            expansion = validation.expansion_query
            if expansion:
                delta["messages"] = [
                    HumanMessage(
                        content=f"Retrieval was not relevant. Try this expanded query: {expansion}"
                    )
                ]
        return delta

    return validate_retrieval_node
