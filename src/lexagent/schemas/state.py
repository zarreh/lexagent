from typing import TypedDict


class SkeletonState(TypedDict):
    """Phase 0 walking-skeleton state — kept as the template's trivial proof graph."""

    message: str
    echoed: str
    done: bool
