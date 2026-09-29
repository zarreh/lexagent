import asyncio

from lexagent.graph.nodes.parse_query import build_parse_query_node
from lexagent.graph.nodes.refuse import refuse_node
from lexagent.graph.nodes.retrieve import build_retrieve_node
from lexagent.retrieval.store import LocalCorpusStore
from lexagent.schemas.legal import LegalAnswer, ParsedQuery
from lexagent.schemas.state import LexAgentState


async def test_parse_query_node_returns_parsed_query() -> None:
    expected = ParsedQuery(
        intent="refund timeline",
        jurisdiction="TX",
        issue_type="security deposit refund",
        in_scope=True,
    )

    class _FakeChain:
        def invoke(self, input: dict[str, str]) -> ParsedQuery:
            return expected

        async def ainvoke(self, input: dict[str, str]) -> ParsedQuery:
            return expected

    node = build_parse_query_node(_FakeChain())
    state: LexAgentState = {
        "messages": [],
        "question": "When does my landlord have to return my deposit in Texas?",
        "parsed_query": None,
        "retrieved_sources": [],
        "retrieval_attempts": 0,
        "verification_attempts": 0,
        "draft_answer": "",
        "claims": [],
        "citation_report": None,
        "answer": None,
        "refusal_reason": None,
        "started_at": 0.0,
    }
    coroutine = node(state)
    assert asyncio.iscoroutine(coroutine)
    result: dict[str, object] = await coroutine
    assert result["parsed_query"] == expected


async def test_retrieve_node_searches_both_corpora() -> None:
    store = LocalCorpusStore()
    node = build_retrieve_node(store)
    state: LexAgentState = {
        "messages": [],
        "question": "security deposit refund",
        "parsed_query": ParsedQuery(
            intent="refund timeline", jurisdiction="TX", issue_type="security deposit refund"
        ),
        "retrieved_sources": [],
        "retrieval_attempts": 0,
        "verification_attempts": 0,
        "draft_answer": "",
        "claims": [],
        "citation_report": None,
        "answer": None,
        "refusal_reason": None,
        "started_at": 0.0,
    }
    coroutine = node(state)
    assert asyncio.iscoroutine(coroutine)
    result: dict[str, object] = await coroutine
    sources = result["retrieved_sources"]
    assert isinstance(sources, list)
    assert len(sources) > 0
    corpora = {s.corpus for s in sources}
    assert corpora == {"statute", "precedent"}


def test_refuse_node_returns_referral() -> None:
    state: LexAgentState = {
        "messages": [],
        "question": "criminal charge",
        "parsed_query": None,
        "retrieved_sources": [],
        "retrieval_attempts": 0,
        "verification_attempts": 0,
        "draft_answer": "",
        "claims": [],
        "citation_report": None,
        "answer": None,
        "refusal_reason": "Out of scope.",
        "started_at": 0.0,
    }
    result = refuse_node(state)
    answer = result["answer"]
    assert isinstance(answer, LegalAnswer)
    assert answer.referral_triggered is True
    assert "Out of scope." in answer.reasoning
