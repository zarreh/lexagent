"""Layer 2 eval: run the full graph and grade the answers.

Deterministic checks (expected statutes cited, no citation outside the retrieved
sources, correct refuse/answer outcome) plus an LLM judge for faithfulness to the
retrieved sources and coverage of key facts. Needs OpenAI (and Qdrant for semantic
retrieval); costs a few cents per run. Usage: `make eval-answers`.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

from lexagent.api.run_executor import _initial_state
from lexagent.graph.builder import build_lexagent_graph
from lexagent.schemas.legal import LegalAnswer, RetrievedSource
from lexagent.settings import get_settings

JUDGE_MODEL = "gpt-4o"

JUDGE_PROMPT = """You grade a legal-research answer against the sources it was given.

Faithfulness (1-5): 5 means every legal assertion in the answer is supported by the
sources; 1 means the answer mostly states things the sources do not support.
Facts correct: true only if the answer states every key fact below correctly.
Judge only against the sources and key facts, not your own legal knowledge."""


@dataclass(frozen=True)
class AnswerScenario:
    id: str
    question: str
    expected_statutes: list[str] = field(default_factory=list)
    key_facts: list[str] = field(default_factory=list)
    expect_refusal: bool = False


SCENARIOS = [
    AnswerScenario(
        "deposit-tx",
        "How long does a Texas landlord have to return my security deposit?",
        ["tx-prop-92.103"],
        [
            "Refund is due within 30 days after the tenant surrenders possession and gives a "
            "forwarding address"
        ],
    ),
    AnswerScenario(
        "deposit-ca",
        "How long does my California landlord have to return my deposit?",
        ["ca-civ-1950.5"],
        ["Within 21 days the landlord must return the remainder with an itemized statement"],
    ),
    AnswerScenario(
        "wear-tear-tx",
        "My Texas landlord kept my whole deposit for normal wear and tear. Is that allowed?",
        ["tx-prop-92.102"],
        ["A landlord may not retain a deposit for normal wear and tear"],
    ),
    AnswerScenario(
        "heater-tx",
        "My landlord keeps ignoring me about the broken heater in Texas.",
        ["tx-prop-92.056", "tx-prop-92.0581"],
        [
            "The landlord must make a diligent effort to repair after notice if rent is current",
            "The tenant may terminate, repair and deduct, or seek judicial remedies",
        ],
    ),
    AnswerScenario(
        "hot-water-ca",
        "My California apartment has had no hot water for two weeks. What can I do?",
        ["ca-civ-1941", "ca-civ-1942"],
        [
            "No hot water is a habitability defect",
            "Repair and deduct is capped at one month's rent",
        ],
    ),
    AnswerScenario(
        "entry-ca",
        "Can the owner just walk into my California apartment whenever he wants?",
        ["ca-civ-1954"],
        ["Entry requires reasonable written notice and normal business hours, except emergencies"],
    ),
    AnswerScenario(
        "retaliation-ca",
        "My California landlord raised my rent right after I complained about repairs.",
        ["ca-civ-1942.5"],
        ["A landlord may not retaliate by raising rent after a tenant exercises legal rights"],
    ),
    AnswerScenario(
        "retaliation-tx",
        "My Texas landlord ended my lease after I reported a repair problem.",
        ["tx-prop-92.331"],
        ["A landlord may not retaliate against a tenant who exercises a right under the chapter"],
    ),
    AnswerScenario(
        "criminal", "I have been charged with a crime. What should I do?", expect_refusal=True
    ),
    AnswerScenario(
        "out-of-state", "My landlord in Florida will not return my deposit.", expect_refusal=True
    ),
]


class Judgement(BaseModel):
    faithfulness: int = Field(ge=1, le=5)
    facts_correct: bool
    notes: str


@dataclass(frozen=True)
class Score:
    scenario: AnswerScenario
    outcome_ok: bool
    cite_recall: float
    hallucinated: list[str]
    faithfulness: int | None
    facts_correct: bool | None


def score_citations(
    answer: LegalAnswer, retrieved: list[RetrievedSource], expected: list[str]
) -> tuple[float, list[str]]:
    """Return (recall of expected statutes among citations, citations not in retrieved)."""
    cited = [c.source_id for c in answer.citations]
    recall = sum(1 for e in expected if e in cited) / len(expected) if expected else 1.0
    known = {s.source_id for s in retrieved}
    return recall, [c for c in cited if c not in known]


async def _judge(
    judge: ChatOpenAI, scenario: AnswerScenario, answer: LegalAnswer, sources: str
) -> Judgement:
    chain = judge.with_structured_output(Judgement)
    result = await chain.ainvoke(
        [
            ("system", JUDGE_PROMPT),
            (
                "human",
                f"Question: {scenario.question}\n\nSources:\n{sources}\n\n"
                f"Answer:\nRights: {answer.rights}\nObligations: {answer.obligations}\n"
                f"Reasoning: {answer.reasoning}\n\nKey facts:\n"
                + "\n".join(f"- {f}" for f in scenario.key_facts),
            ),
        ]
    )
    assert isinstance(result, Judgement)
    return result


async def _run_one(graph: object, judge: ChatOpenAI, scenario: AnswerScenario) -> Score:
    state = await graph.ainvoke(_initial_state(scenario.question))  # type: ignore[attr-defined]
    answer: LegalAnswer | None = state.get("answer")
    if answer is None:
        return Score(scenario, False, 0.0, [], None, None)
    if scenario.expect_refusal:
        return Score(scenario, answer.referral_triggered, 1.0, [], None, None)

    retrieved: list[RetrievedSource] = state["retrieved_sources"]
    recall, hallucinated = score_citations(answer, retrieved, scenario.expected_statutes)
    sources = "\n".join(f"[{s.source_id}] {s.title}: {s.text}" for s in retrieved)
    judgement = await _judge(judge, scenario, answer, sources)
    return Score(
        scenario,
        not answer.referral_triggered,
        recall,
        hallucinated,
        judgement.faithfulness,
        judgement.facts_correct,
    )


async def main() -> int:
    settings = get_settings()
    if not settings.openai_api_key:
        print("LEXAGENT_OPENAI_API_KEY is required for answer evals.")
        return 2
    graph = build_lexagent_graph(settings)
    judge = ChatOpenAI(model=JUDGE_MODEL, temperature=0, api_key=SecretStr(settings.openai_api_key))
    scores = await asyncio.gather(*(_run_one(graph, judge, s) for s in SCENARIOS))

    print(f"{'Scenario':<16} {'Outcome':>8} {'CiteRec':>8} {'Halluc':>7} {'Faith':>6} {'Facts':>6}")
    print("-" * 56)
    for s in scores:
        faith = "-" if s.faithfulness is None else str(s.faithfulness)
        facts = "-" if s.facts_correct is None else ("yes" if s.facts_correct else "NO")
        print(
            f"{s.scenario.id:<16} {'ok' if s.outcome_ok else 'WRONG':>8} {s.cite_recall:>8.2f} "
            f"{len(s.hallucinated):>7} {faith:>6} {facts:>6}"
        )
    graded = [s for s in scores if s.faithfulness is not None]
    mean_faith = sum(s.faithfulness or 0 for s in graded) / len(graded)
    facts_rate = sum(1 for s in graded if s.facts_correct) / len(graded)
    cite_recall = sum(s.cite_recall for s in scores) / len(scores)
    hallucinated = sum(len(s.hallucinated) for s in scores)
    outcomes = sum(1 for s in scores if s.outcome_ok) / len(scores)
    print("-" * 56)
    print(
        f"outcomes {outcomes:.2f} | cite recall {cite_recall:.2f} | hallucinated {hallucinated} "
        f"| faithfulness {mean_faith:.2f}/5 | facts {facts_rate:.2f}"
    )
    passed = outcomes == 1.0 and hallucinated == 0 and mean_faith >= 4.0 and facts_rate >= 0.8
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
