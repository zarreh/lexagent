from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from lexagent.api.deps import get_compiled_graph
from lexagent.api.rate_limit import DEFAULT_RATE_LIMIT, limiter
from lexagent.api.streaming import stream_graph_events
from lexagent.graph.builder import SkeletonGraph
from lexagent.schemas.state import SkeletonState

router = APIRouter(prefix="/ask", tags=["ask"])

GraphDep = Annotated[SkeletonGraph, Depends(get_compiled_graph)]


@router.get("/skeleton/events")
@limiter.limit(DEFAULT_RATE_LIMIT)
async def skeleton_events(
    request: Request, graph: GraphDep, message: str = "hello"
) -> EventSourceResponse:
    """Phase 0 proof: streams the trivial echo -> done graph node-by-node."""
    initial_state: SkeletonState = {"message": message, "echoed": "", "done": False}
    return EventSourceResponse(stream_graph_events(graph, initial_state))
