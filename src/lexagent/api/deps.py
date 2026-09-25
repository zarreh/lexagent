from functools import lru_cache
from pathlib import Path

from lexagent.graph.builder import (
    LexAgentGraph,
    SkeletonGraph,
    build_lexagent_graph,
    build_skeleton_graph,
)
from lexagent.settings import Settings, get_settings
from lexagent.store.run_store import RunStore


def settings_dependency() -> Settings:
    return get_settings()


@lru_cache
def get_compiled_graph() -> SkeletonGraph:
    """Single compiled-graph instance, shared across requests."""
    return build_skeleton_graph()


@lru_cache
def get_lexagent_graph() -> LexAgentGraph:
    """Single compiled real reasoning graph, shared across requests.
    Overridden in tests via `app.dependency_overrides`.
    """
    return build_lexagent_graph(get_settings())


@lru_cache
def get_run_store() -> RunStore:
    return RunStore(Path(get_settings().run_store_path))
