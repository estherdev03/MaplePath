"""Tests for noc.evaluate.EvaluateService."""

from unittest.mock import MagicMock

from db.models import NOC
from noc.evaluate import (
    EvaluateService,
    _hash_labels_file,
    noc_retrieval_method_evaluate,
)
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


# ---- _hash_labels_file ----
def test_hash_labels_file_is_stable_and_content_sensitive(tmp_path):
    file_a = tmp_path / "a.csv"
    file_a.write_text("same content")
    file_b = tmp_path / "b.csv"
    file_b.write_text("same content")
    file_c = tmp_path / "c.csv"
    file_c.write_text("different content")

    assert _hash_labels_file(str(file_a)) == _hash_labels_file(str(file_a))
    assert _hash_labels_file(str(file_a)) == _hash_labels_file(str(file_b))
    assert _hash_labels_file(str(file_a)) != _hash_labels_file(str(file_c))


# ---- noc_retrieval_method_evaluate caching ----
def _labels_csv(tmp_path):
    labels_file = tmp_path / "labels.csv"
    labels_file.write_text(
        "query_id,job_title,job_responsibility,noc_code,minor_group_code,major_group_code,noc_title,case_type\n"
        "1,Dev,resp,11111,1000,10,t,exact_title\n"
    )
    return labels_file


def test_noc_retrieval_method_evaluate_returns_cached_run_without_recomputing(
    tmp_path, monkeypatch
):
    labels_file = _labels_csv(tmp_path)
    monkeypatch.setattr("noc.evaluate.DatabaseService", MagicMock())

    cached_run = MagicMock()
    cached_run.examples_report = [
        {
            "case_type": "exact_title",
            "job_title": "Dev",
            "bm25": [0.5, 1],
            "vector": [0.6, 1],
            "rrf": [0.7, 1],
            "hybrid": [0.8, 1],
        }
    ]
    cached_run.mean_report = {
        "bm25": [0.5, 1],
        "vector": [0.6, 1],
        "rrf": [0.7, 1],
        "hybrid": [0.8, 1],
    }
    mock_repo = MagicMock()
    mock_repo.get_by_hash.return_value = cached_run
    monkeypatch.setattr(
        "noc.evaluate.EvaluateRepository", MagicMock(return_value=mock_repo)
    )
    mock_noc_service_cls = MagicMock()
    monkeypatch.setattr("noc.evaluate.NOCService", mock_noc_service_cls)

    examples_report, mean_report = noc_retrieval_method_evaluate(str(labels_file))

    assert examples_report.report[0].job_title == "Dev"
    assert mean_report.hybrid == [0.8, 1]
    mock_noc_service_cls.assert_not_called()
    mock_repo.save.assert_not_called()


def test_noc_retrieval_method_evaluate_computes_and_caches_on_miss(
    tmp_path, monkeypatch
):
    labels_file = _labels_csv(tmp_path)
    monkeypatch.setattr("noc.evaluate.DatabaseService", MagicMock())
    monkeypatch.setattr("noc.evaluate.NOCRepository", MagicMock())

    mock_repo = MagicMock()
    mock_repo.get_by_hash.return_value = None
    monkeypatch.setattr(
        "noc.evaluate.EvaluateRepository", MagicMock(return_value=mock_repo)
    )

    match = _noc("11111")
    mock_noc_service = MagicMock()
    mock_noc_service.noc_keyword_search.return_value = [match]
    mock_noc_service.noc_semantic_search.return_value = [match]
    mock_noc_service.noc_hybrid_search.return_value = [match]
    mock_noc_service._rrf.return_value = [match]
    mock_noc_service.get_ideal_pool_count.return_value = (0, 0)
    monkeypatch.setattr(
        "noc.evaluate.NOCService", MagicMock(return_value=mock_noc_service)
    )

    examples_report, mean_report = noc_retrieval_method_evaluate(str(labels_file))

    # The evaluation divides by the number of examples in the file,
    # so a single perfect-match row yields the full 1.0 for the mean.
    assert mean_report.hybrid == (1.0, 1.0)
    assert examples_report.report[0].hybrid == (1.0, 1)
    mock_repo.save.assert_called_once()
    saved_hash, saved_examples, saved_mean = mock_repo.save.call_args[0]
    assert saved_hash == _hash_labels_file(str(labels_file))
    assert saved_mean["hybrid"] == (1.0, 1.0)
    assert saved_examples[0]["job_title"] == "Dev"
