from lexagent.graph.edges import route_after_parse, route_after_verify
from lexagent.schemas.legal import CitationReport, ClaimJudgment, ParsedQuery
from lexagent.schemas.state import LexAgentState


def _state(**overrides: object) -> LexAgentState:
    defaults: LexAgentState = {
        "messages": [],
        "question": "",
        "parsed_query": None,
        "retrieved_sources": [],
        "retrieval_attempts": 0,
        "draft_answer": "",
        "claims": [],
        "citation_report": None,
        "answer": None,
        "refusal_reason": None,
        "started_at": 0.0,
    }
    defaults.update(overrides)  # type: ignore[typeddict-item]
    return defaults


def test_route_after_parse_out_of_scope() -> None:
    state = _state(parsed_query=ParsedQuery(intent="", in_scope=False, issue_type=""))
    assert route_after_parse(state) == "refuse"


def test_route_after_parse_in_scope() -> None:
    state = _state(parsed_query=ParsedQuery(intent="", in_scope=True, issue_type=""))
    assert route_after_parse(state) == "retrieve"


def test_route_after_verify_unsupported_returns_reason() -> None:
    report = CitationReport(
        claims=[ClaimJudgment(claim_id="c1", supported=False, reason="missing source")],
        unsupported=1,
        confidence="low",
    )
    state = _state(citation_report=report, retrieval_attempts=1)
    assert route_after_verify(state) == "reason"


def test_route_after_verify_zero_unsupported_publishes() -> None:
    report = CitationReport(claims=[], unsupported=0, confidence="high")
    state = _state(citation_report=report)
    assert route_after_verify(state) == "publish"
