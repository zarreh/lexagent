"""Canonical retrieval scenarios for LexAgent.

Each scenario states a question, the expected jurisdiction, and the statutes or
precedents that a well-performing retrieval layer should surface. These are
used to compute recall-oriented metrics without invoking an LLM.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalScenario:
    id: str
    question: str
    jurisdiction: str
    expected_statutes: list[str]
    expected_precedents: list[str]


CANONICAL_SCENARIOS: list[RetrievalScenario] = [
    RetrievalScenario(
        id="deposit-tx",
        question="My Texas landlord kept my security deposit for normal wear and tear.",
        jurisdiction="TX",
        expected_statutes=["tx-prop-92.104"],
        expected_precedents=["SYN-0001"],
    ),
    RetrievalScenario(
        id="repair-ca",
        question="My California apartment has no hot water and the landlord has not fixed it.",
        jurisdiction="CA",
        expected_statutes=["ca-civ-1941.1", "ca-civ-1942"],
        expected_precedents=["SYN-0010"],
    ),
    RetrievalScenario(
        id="eviction-notice-tx",
        question="I got an oral eviction notice in Texas. Is that valid?",
        jurisdiction="TX",
        expected_statutes=["tx-prop-24.005"],
        expected_precedents=["SYN-0002"],
    ),
    RetrievalScenario(
        id="retaliation-ca",
        question=(
            "My California landlord is retaliating by increasing rent "
            "after I exercised my tenant rights."
        ),
        jurisdiction="CA",
        expected_statutes=["ca-civ-1942.5"],
        expected_precedents=["SYN-0011"],
    ),
    RetrievalScenario(
        id="lockout-tx",
        question="My Texas landlord changed my locks and will not give me a key.",
        jurisdiction="TX",
        expected_statutes=["tx-prop-92.0081"],
        expected_precedents=["SYN-0004"],
    ),
]


# Everyday phrasing that shares few words with the statute text; probes semantic recall.
PARAPHRASE_SCENARIOS: list[RetrievalScenario] = [
    RetrievalScenario(
        id="heater-tx",
        question="My landlord keeps ignoring me about the broken heater.",
        jurisdiction="TX",
        expected_statutes=["tx-prop-92.052", "tx-prop-92.056"],
        expected_precedents=[],
    ),
    RetrievalScenario(
        id="walk-in-ca",
        question="Can the owner just walk into my apartment whenever he wants?",
        jurisdiction="CA",
        expected_statutes=["ca-civ-1954"],
        expected_precedents=[],
    ),
    RetrievalScenario(
        id="kicked-out-ca",
        question="They threw me out right after I complained about mold.",
        jurisdiction="CA",
        expected_statutes=["ca-civ-1942.5"],
        expected_precedents=[],
    ),
    RetrievalScenario(
        id="money-back-tx",
        question="How soon do I get my money back after I move out?",
        jurisdiction="TX",
        expected_statutes=["tx-prop-92.103"],
        expected_precedents=[],
    ),
]
