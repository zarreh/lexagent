"""Retrieval-quality metrics for LexAgent evals."""

from __future__ import annotations

from dataclasses import dataclass

from evals.scenarios import CANONICAL_SCENARIOS, RetrievalScenario
from lexagent.retrieval.store import CorpusStore


@dataclass(frozen=True)
class ScenarioResult:
    scenario: RetrievalScenario
    statute_recall: float
    precedent_recall: float
    combined_recall: float


@dataclass(frozen=True)
class MetricsReport:
    scenario_results: list[ScenarioResult]
    mean_statute_recall: float
    mean_precedent_recall: float
    mean_combined_recall: float


def _recall(expected: list[str], retrieved_ids: list[str]) -> float:
    if not expected:
        return 1.0
    found = sum(1 for source_id in expected if source_id in retrieved_ids)
    return found / len(expected)


def evaluate_retrieval(
    store: CorpusStore,
    top_k: int = 4,
) -> MetricsReport:
    """Evaluate the local corpus store against the canonical scenarios."""
    results: list[ScenarioResult] = []
    for scenario in CANONICAL_SCENARIOS:
        statutes = store.search(scenario.question, scenario.jurisdiction, "statute", top_k=top_k)
        precedents = store.search(
            scenario.question, scenario.jurisdiction, "precedent", top_k=top_k
        )
        statute_recall = _recall(scenario.expected_statutes, [s.source_id for s in statutes])
        precedent_recall = _recall(scenario.expected_precedents, [p.source_id for p in precedents])
        combined = (statute_recall + precedent_recall) / 2
        results.append(
            ScenarioResult(
                scenario=scenario,
                statute_recall=statute_recall,
                precedent_recall=precedent_recall,
                combined_recall=combined,
            )
        )

    def mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    return MetricsReport(
        scenario_results=results,
        mean_statute_recall=mean([r.statute_recall for r in results]),
        mean_precedent_recall=mean([r.precedent_recall for r in results]),
        mean_combined_recall=mean([r.combined_recall for r in results]),
    )


def print_report(report: MetricsReport) -> None:
    print(f"{'Scenario':<20} {'Statute':>8} {'Precedent':>10} {'Combined':>10}")
    print("-" * 52)
    for result in report.scenario_results:
        print(
            f"{result.scenario.id:<20} "
            f"{result.statute_recall:>8.2f} "
            f"{result.precedent_recall:>10.2f} "
            f"{result.combined_recall:>10.2f}"
        )
    print("-" * 52)
    print(
        f"{'MEAN':<20} "
        f"{report.mean_statute_recall:>8.2f} "
        f"{report.mean_precedent_recall:>10.2f} "
        f"{report.mean_combined_recall:>10.2f}"
    )
