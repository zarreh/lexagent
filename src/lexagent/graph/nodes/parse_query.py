"""Parse the user's question into a structured query."""

from __future__ import annotations

from collections.abc import Callable

from lexagent.graph.protocols import ParseQueryChain
from lexagent.schemas.state import LexAgentState


def build_parse_query_node(
    chain: ParseQueryChain,
) -> Callable[[LexAgentState], dict[str, object]]:
    def parse_query_node(state: LexAgentState) -> dict[str, object]:
        parsed = chain.invoke({"question": state["question"]})
        return {"parsed_query": parsed}

    return parse_query_node
