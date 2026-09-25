"""Execute one LexAgent query run and persist events to the RunStore."""

from __future__ import annotations

import json

import structlog
from pydantic import BaseModel
from zarreh_agentkit.observability import build_tracing_callbacks

from lexagent.graph.builder import LexAgentGraph
from lexagent.observability import get_logger
from lexagent.schemas.legal import LegalAnswer
from lexagent.schemas.state import LexAgentState
from lexagent.settings import Settings
from lexagent.store.run_store import RunStore

logger = get_logger(__name__)

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


def _json_default(value: object) -> object:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return str(value)


def _initial_state(question: str) -> LexAgentState:
    import time

    return LexAgentState(
        messages=[],
        question=question,
        parsed_query=None,
        retrieved_sources=[],
        retrieval_attempts=0,
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
    structlog.contextvars.bind_contextvars(correlation_id=run_id)
    try:
        callbacks = build_tracing_callbacks(settings.langsmith_api_key, settings.langsmith_project)
        final_state: dict[str, object] = {}
        sequence = 0

        async for event in graph.astream_events(
            _initial_state(question),
            version="v2",
            config={"callbacks": callbacks, "metadata": {"correlation_id": run_id}},
        ):
            if event["event"] != "on_chain_end":
                continue
            metadata = event.get("metadata") or {}
            node_name = metadata.get("langgraph_node")
            if node_name not in _GRAPH_NODE_NAMES:
                continue

            output: dict[str, object] = event.get("data", {}).get("output", {}) or {}
            payload = json.dumps(output, default=_json_default)
            run_store.append_event(run_id, sequence, node_name, payload)
            sequence += 1
            final_state.update(output)

        answer = final_state.get("answer")
        if isinstance(answer, LegalAnswer):
            outcome = _outcome_kind(answer)
            run_store.complete_run(
                run_id, outcome, json.dumps(answer.model_dump(mode="json"), default=_json_default)
            )
        elif final_state.get("refusal_reason"):
            run_store.fail_run(run_id, str(final_state.get("refusal_reason")))
        else:
            run_store.fail_run(run_id, "Graph finished without an answer.")
    except Exception as exc:  # noqa: BLE001
        logger.exception("query_failed", run_id=run_id)
        run_store.fail_run(run_id, str(exc))
