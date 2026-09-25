from functools import lru_cache

from lexagent.graph.builder import SkeletonGraph, build_skeleton_graph
from lexagent.settings import get_settings


def settings_dependency() -> object:
    return get_settings()


@lru_cache
def get_compiled_graph() -> SkeletonGraph:
    """Single compiled-graph instance, shared across requests."""
    return build_skeleton_graph()
