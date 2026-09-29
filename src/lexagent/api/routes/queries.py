"""Query lifecycle routes."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lexagent.api.deps import get_lexagent_graph, get_run_store, settings_dependency
from lexagent.api.run_executor import execute_query
from lexagent.api.schemas import QueryResponse
from lexagent.graph.builder import LexAgentGraph
from lexagent.schemas.legal import LegalAnswer
from lexagent.settings import Settings
from lexagent.store.run_store import RunStore

router = APIRouter(prefix="/queries", tags=["queries"])


class QueryRequest(BaseModel):
    question: str


class QueryCreatedResponse(BaseModel):
    id: str
    status: str


@router.post("", response_model=QueryCreatedResponse, status_code=202)
def create_query(
    request: Request,
    payload: QueryRequest,
    background_tasks: BackgroundTasks,
    graph: Annotated[LexAgentGraph, Depends(get_lexagent_graph)],
    run_store: Annotated[RunStore, Depends(get_run_store)],
    settings: Annotated[Settings, Depends(settings_dependency)],
) -> QueryCreatedResponse:
    run_id = str(uuid.uuid4())
    run_store.create_run(run_id, payload.question)
    background_tasks.add_task(execute_query, run_id, payload.question, graph, run_store, settings)
    return QueryCreatedResponse(id=run_id, status="running")


@router.get("/{run_id}", response_model=QueryResponse)
def get_query(
    run_id: str,
    run_store: Annotated[RunStore, Depends(get_run_store)],
) -> QueryResponse:
    run = run_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Query not found")
    answer = LegalAnswer.model_validate_json(run.answer_json) if run.answer_json else None
    return QueryResponse(
        id=run.id,
        question=run.question,
        status=run.status,
        created_at=run.created_at,
        updated_at=run.updated_at,
        outcome_kind=run.outcome_kind,
        answer=answer,
        error=run.error,
    )


async def _event_stream(
    run_store: RunStore,
    run_id: str,
    poll_interval: float,
) -> AsyncGenerator[str, None]:
    seen = 0
    while True:
        run = run_store.get_run(run_id)
        if run is None:
            yield f"event: error\ndata: {run_id} not found\n\n"
            break

        events = run_store.get_events(run_id, after_sequence=seen - 1)
        for event in events:
            yield f"event: {event.node}\ndata: {event.payload_json}\n\n"
            seen += 1

        if run.status in ("completed", "failed"):
            payload = '{"status": "' + run.status + '"}'
            yield f"event: done\ndata: {payload}\n\n"
            break

        await asyncio.sleep(poll_interval)


@router.get("/{run_id}/events")
def query_events(
    run_id: str,
    request: Request,
    run_store: Annotated[RunStore, Depends(get_run_store)],
    poll_interval: Annotated[float, Query(gt=0)] = 0.5,
) -> StreamingResponse:
    if run_store.get_run(run_id) is None:
        raise HTTPException(status_code=404, detail="Query not found")

    async def stream() -> AsyncGenerator[str, None]:
        async for chunk in _event_stream(run_store, run_id, poll_interval):
            yield chunk

    return StreamingResponse(stream(), media_type="text/event-stream")
