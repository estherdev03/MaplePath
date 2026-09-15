"""Tests for noc.evaluate.EvaluateService.

noc_retrieval_method_evaluate itself constructs its own DatabaseService/
NOCRepository/NOCService internally, which makes it untestable without a
live DB (see the skipped placeholder below) -- out of scope here.
"""

from unittest.mock import MagicMock

from db.models import NOC
from noc.evaluate import EvaluateService, noc_retrieval_method_evaluate
from noc.types import IdealNOC


def _noc(code, minor="1000", major="10"):
    return NOC(noc_code=code, minor_group_code=minor, major_group_code=major)


def _service(minor_count=0, major_count=0):
    noc_service = MagicMock()
    noc_service.get_ideal_pool_count.return_value = (minor_count, major_count)
    return EvaluateService(noc_service)


def test_ndcg_evaluate_perfect_ranking_returns_one():
    service = _service()
    ideal = IdealNOC(noc_code="11111", minor_group_code="1000", major_group_code="10")
    assert service.ndcg_evaluate([_noc("11111")], ideal, k=1) == 1.0


def test_ndcg_evaluate_no_relevant_results_returns_zero():
    service = _service()
    ideal = IdealNOC(noc_code="11111", minor_group_code="1000", major_group_code="10")
    result = service.ndcg_evaluate(
        [_noc("99999", minor="9999", major="99")], ideal, k=1
    )
    assert result == 0.0


def test_ndcg_evaluate_relevance_by_exact_minor_and_major_match():
    """Exact noc_code match outranks a minor-group-only match, which
    outranks a major-group-only match (relevance 3/2/1)."""
    service = _service(minor_count=1, major_count=1)
    ideal = IdealNOC(noc_code="11111", minor_group_code="1000", major_group_code="10")

    exact = service.ndcg_evaluate([_noc("11111")], ideal, k=3)
    minor_only = service.ndcg_evaluate([_noc("22222", minor="1000")], ideal, k=3)
    major_only = service.ndcg_evaluate(
        [_noc("33333", minor="2000", major="10")], ideal, k=3
    )
    assert exact > minor_only > major_only > 0


def test_ndcg_evaluate_truncates_to_k():
    service = _service()
    ideal = IdealNOC(noc_code="11111", minor_group_code="1000", major_group_code="10")
    # The one relevant hit sits past k=1, so it's excluded from scoring.
    irrelevant = _noc("99999", minor="9999", major="99")
    result = service.ndcg_evaluate([irrelevant, _noc("11111")], ideal, k=1)
    assert result == 0.0


def test_calculate_hit_rate_present_absent_and_empty():
    service = EvaluateService(MagicMock())
    ideal = IdealNOC(noc_code="11111", minor_group_code="1000", major_group_code="10")
    assert service.calculate_hit_rate([_noc("99999"), _noc("11111")], ideal) == 1
    assert service.calculate_hit_rate([_noc("99999")], ideal) == 0
    assert service.calculate_hit_rate([], ideal) == 0
