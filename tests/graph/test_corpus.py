import re

from data.seed_precedents import all_precedents
from data.seed_statutes import all_statutes
from evals.answer_eval import SCENARIOS
from evals.scenarios import CANONICAL_SCENARIOS, PARAPHRASE_SCENARIOS

_PREFIX = {"TX": "tx-prop-", "CA": "ca-civ-"}


def _ids() -> set[str]:
    return {s.id for s in all_statutes()}


def test_statute_ids_are_unique() -> None:
    ids = [s.id for s in all_statutes()]
    assert len(ids) == len(set(ids))


def test_precedents_only_cite_sections_in_the_corpus() -> None:
    ids = _ids()
    for case in all_precedents():
        text = f"{case.facts} {case.holding}"
        for number in re.findall(r"(?<![\d$,])(\d{2,5}\.\d{1,4})", text):
            assert f"{_PREFIX[case.jurisdiction]}{number}" in ids, (case.case_id, number)


def test_eval_expectations_exist_in_the_corpus() -> None:
    ids = _ids()
    precedent_ids = {p.case_id for p in all_precedents()}
    for scenario in CANONICAL_SCENARIOS + PARAPHRASE_SCENARIOS:
        assert set(scenario.expected_statutes) <= ids, scenario.id
        assert set(scenario.expected_precedents) <= precedent_ids, scenario.id
    for answer_scenario in SCENARIOS:
        assert set(answer_scenario.expected_statutes) <= ids, answer_scenario.id
