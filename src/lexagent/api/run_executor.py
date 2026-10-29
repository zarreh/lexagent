"""Execute one LexAgent query run and persist events to the RunStore."""

from __future__ import annotations

import json
from typing import Any

from zarreh_agentkit.observability import build_tracing_callbacks
from zarreh_agentkit.runs import execute_run

from lexagent.graph.builder import LexAgentGraph
from lexagent.schemas.legal import LegalAnswer
from lexagent.schemas.state import LexAgentState
from lexagent.settings import Settings
from lexagent.store.run_store import RunStore

_GRAPH_NODE_NAMES = frozenset(
    {
        "parse_query",
        "retrieve",
        "validate_retrieval",
        "reason",
        "extract_claims",
        "verify_citations",
        "publish",
        "refuse",
        "budget_exceeded",
    }
)


def _initial_state(question: str) -> LexAgentState:
    import time

    return LexAgentState(
        messages=[],
        question=question,
        parsed_query=None,
        retrieved_sources=[],
        retrieval_attempts=0,
        verification_attempts=0,
        draft_answer="",
        claims=[],
        citation_report=None,
        answer=None,
        refusal_reason=None,
        started_at=time.time(),
    )


def _outcome_kind(answer: LegalAnswer | None) -> str:
    if answer is None:
        return "incomplete"
    if answer.referral_triggered:
        return "refusal"
    return "answer"


async def execute_query(
    run_id: str,
    question: str,
    graph: LexAgentGraph,
    run_store: RunStore,
    settings: Settings,
) -> None:
    def finalize(final_state: dict[str, Any]) -> None:
        answer = final_state.get("answer")
        if isinstance(answer, LegalAnswer):
            run_store.complete_run(
                run_id, _outcome_kind(answer), json.dumps(answer.model_dump(mode="json"))
            )
        elif final_state.get("refusal_reason"):
            run_store.fail_run(run_id, str(final_state.get("refusal_reason")))
        else:
            run_store.fail_run(run_id, "Graph finished without an answer.")

    await execute_run(
        run_id=run_id,
        graph=graph,
        graph_input=_initial_state(question),
        store=run_store,
        finalize=finalize,
        callbacks=build_tracing_callbacks(settings.langsmith_api_key, settings.langsmith_project),
        node_names=_GRAPH_NODE_NAMES,
    )
