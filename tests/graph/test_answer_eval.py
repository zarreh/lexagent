from evals.answer_eval import score_citations
from lexagent.schemas.legal import Citation, LegalAnswer, RetrievedSource


def _answer(*ids: str) -> LegalAnswer:
    return LegalAnswer(
        rights="r",
        obligations="o",
        reasoning="x",
        citations=[Citation(source_id=i, corpus="statute") for i in ids],
        confidence="high",
        referral_triggered=False,
    )


def _source(source_id: str) -> RetrievedSource:
    return RetrievedSource(
        source_id=source_id, corpus="statute", jurisdiction="TX", title="t", text="x"
    )


def test_score_citations_full_recall_no_hallucination() -> None:
    recall, bad = score_citations(_answer("a", "b"), [_source("a"), _source("b")], ["a", "b"])
    assert recall == 1.0
    assert bad == []


def test_score_citations_flags_unretrieved_and_missing() -> None:
    recall, bad = score_citations(_answer("a", "zzz"), [_source("a")], ["a", "b"])
    assert recall == 0.5
    assert bad == ["zzz"]
