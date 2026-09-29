from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from lexagent.graph.chains.citation_verifier import build_citation_verifier_chain
from lexagent.graph.chains.claim_extractor import build_claim_extractor_chain
from lexagent.graph.chains.parse_query import build_parse_query_chain
from lexagent.graph.chains.reason import build_reason_chain
from lexagent.graph.chains.validate_retrieval import build_validate_retrieval_chain
from lexagent.graph.edges import (
    route_after_parse,
    route_after_validate,
    route_after_verify,
)
from lexagent.graph.nodes.budget_exceeded import budget_exceeded_node
from lexagent.graph.nodes.done import done_node
from lexagent.graph.nodes.echo import echo_node
from lexagent.graph.nodes.extract_claims import build_extract_claims_node
from lexagent.graph.nodes.parse_query import build_parse_query_node
from lexagent.graph.nodes.publish import publish_node
from lexagent.graph.nodes.reason import build_reason_node
from lexagent.graph.nodes.refuse import refuse_node
from lexagent.graph.nodes.retrieve import build_retrieve_node
from lexagent.graph.nodes.validate_retrieval import build_validate_retrieval_node
from lexagent.graph.nodes.verify_citations import build_verify_citations_node
from lexagent.graph.policies import build_fast_model, build_reasoning_model
from lexagent.retrieval.store import CorpusStore, build_store
from lexagent.schemas.state import LexAgentState, SkeletonState
from lexagent.settings import Settings

SkeletonGraph = CompiledStateGraph[SkeletonState, None, SkeletonState, SkeletonState]
LexAgentGraph = CompiledStateGraph[LexAgentState, None, LexAgentState, LexAgentState]


def build_skeleton_graph() -> SkeletonGraph:
    """Phase 0 proof graph: echo -> done."""
    workflow = StateGraph(SkeletonState)
    workflow.add_node("echo", echo_node)
    workflow.add_node("done", done_node)
    workflow.set_entry_point("echo")
    workflow.add_edge("echo", "done")
    workflow.add_edge("done", END)
    return workflow.compile()


def build_lexagent_graph(
    settings: Settings,
    store: CorpusStore | None = None,
) -> LexAgentGraph:
    """The full dual-corpus legal-reasoning graph."""
    if store is None:
        store = build_store(settings)

    fast_model = build_fast_model(settings)
    reasoning_model = build_reasoning_model(settings)

    parse_query_chain = build_parse_query_chain(fast_model)
    validate_retrieval_chain = build_validate_retrieval_chain(fast_model)
    reason_chain = build_reason_chain(reasoning_model)
    claim_extractor_chain = build_claim_extractor_chain(fast_model)
    citation_verifier_chain = build_citation_verifier_chain(reasoning_model)

    workflow = StateGraph(LexAgentState)
    # mypy cannot resolve add_node overloads against factory-returned
    # Callables; each node is unit-tested directly. Cast to RunnableChain.
    workflow.add_node("parse_query", build_parse_query_node(parse_query_chain))  # type: ignore[arg-type]
    workflow.add_node("retrieve", build_retrieve_node(store))  # type: ignore[arg-type]
    workflow.add_node("validate_retrieval", build_validate_retrieval_node(validate_retrieval_chain))  # type: ignore[arg-type]
    workflow.add_node("reason", build_reason_node(reason_chain))  # type: ignore[arg-type]
    workflow.add_node("extract_claims", build_extract_claims_node(claim_extractor_chain))  # type: ignore[arg-type]
    workflow.add_node("verify_citations", build_verify_citations_node(citation_verifier_chain))  # type: ignore[arg-type]
    workflow.add_node("publish", publish_node)
    workflow.add_node("refuse", refuse_node)
    workflow.add_node("budget_exceeded", budget_exceeded_node)

    workflow.add_edge(START, "parse_query")
    workflow.add_conditional_edges("parse_query", route_after_parse)
    workflow.add_edge("retrieve", "validate_retrieval")
    workflow.add_conditional_edges("validate_retrieval", route_after_validate)
    workflow.add_edge("reason", "extract_claims")
    workflow.add_edge("extract_claims", "verify_citations")
    workflow.add_conditional_edges("verify_citations", route_after_verify)
    workflow.add_edge("publish", END)
    workflow.add_edge("refuse", END)
    workflow.add_edge("budget_exceeded", END)

    return workflow.compile()
