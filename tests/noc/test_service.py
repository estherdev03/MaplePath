"""Tests for noc.service.NOCService."""

from unittest.mock import MagicMock

import pytest
from bs4 import BeautifulSoup
from cohere.errors import TooManyRequestsError

from db.models import NOC
from noc.service import NOCService
from noc.types import EmbeddingInfo, IdealNOC


def _service(repository=None):
    return NOCService(noc_repository=repository or MagicMock())


# ---- _rrf ----
def test_rrf_fuses_weights_dedupes_and_sorts_descending():
    """Vector list weighted 1.0, keyword list weighted 0.5; a NOC present in
    both lists is deduplicated and its scores summed; result sorted desc."""
    noc_a, noc_b, noc_c = NOC(noc_code="A"), NOC(noc_code="B"), NOC(noc_code="C")
    service = _service()
    result = service._rrf(vector_result=[noc_a, noc_b], keyword_result=[noc_b, noc_c])
    assert [n.noc_code for n in result] == ["B", "A", "C"]


def test_rrf_handles_empty_lists():
    noc_a = NOC(noc_code="A")
    service = _service()
    assert [n.noc_code for n in service._rrf([], [noc_a])] == ["A"]
    assert [n.noc_code for n in service._rrf([noc_a], [])] == ["A"]


# ---- _get_list_after_heading ----
def test_get_list_after_heading_returns_list_items_or_empty():
    html = """
    <section><h4>Main duties</h4><ul><li>Do a thing</li><li>Do another</li></ul></section>
    """
    soup = BeautifulSoup(html, "html.parser")
    service = _service()
    assert service._get_list_after_heading(soup, "Main duties") == [
        "Do a thing",
        "Do another",
    ]
    assert service._get_list_after_heading(soup, "Missing heading") == []


# ---- _create_embedding ----
def test_create_embedding_combines_fields_and_calls_embed_query(monkeypatch):
    fake_embed_model = MagicMock()
    fake_embed_model.embed_query.return_value = [0.1, 0.2]
    monkeypatch.setattr(
        "noc.service.OpenAIEmbeddings", MagicMock(return_value=fake_embed_model)
    )
    service = _service()
    info = EmbeddingInfo(
        noc_code="1",
        title="Software Engineer",
        description="d",
        example_titles=[],
        inclusions=[],
        main_duties=[],
        employment_requirements=[],
        additional_information=[],
        exclusions=[],
    )
    text, embedding = service._create_embedding(info)
    assert "noc_code: 1" in text
    assert "title: Software Engineer" in text
    assert embedding == [0.1, 0.2]
    fake_embed_model.embed_query.assert_called_once_with(text)


# ---- noc_semantic_search ----
def test_noc_semantic_search_embeds_query_and_delegates_to_repository(monkeypatch):
    fake_embed_model = MagicMock()
    fake_embed_model.embed_query.return_value = [0.1, 0.2]
    monkeypatch.setattr(
        "noc.service.OpenAIEmbeddings", MagicMock(return_value=fake_embed_model)
    )
    repo = MagicMock()
    repo.vector_search.return_value = ["result"]
    service = _service(repo)

    result = service.noc_semantic_search("software engineer")

    fake_embed_model.embed_query.assert_called_once_with("software engineer")
    repo.vector_search.assert_called_once_with([0.1, 0.2])
    assert result == ["result"]


# ---- noc_keyword_search ----
def test_noc_keyword_search_delegates_to_repository():
    repo = MagicMock()
    repo.keyword_search.return_value = ["result"]
    service = _service(repo)
    assert service.noc_keyword_search("query") == ["result"]
    repo.keyword_search.assert_called_once_with("query")


# ---- noc_hybrid_search ----
def test_noc_hybrid_search_reranks_and_returns_top_10(monkeypatch):
    """Mock rerank_engine.rerank; assert returned order follows the
    reranked ["index"] values mapped back into the RRF result list."""
    service = _service()
    noc_a = NOC(noc_code="A", title="A", main_duties=[], example_titles=[])
    noc_b = NOC(noc_code="B", title="B", main_duties=[], example_titles=[])
    monkeypatch.setattr(service, "noc_semantic_search", lambda q: [noc_a, noc_b])
    monkeypatch.setattr(service, "noc_keyword_search", lambda q: [])
    service.rerank_engine = MagicMock()
    service.rerank_engine.rerank.return_value = [{"index": 1}, {"index": 0}]

    result = service.noc_hybrid_search("query")

    assert [n.noc_code for n in result] == ["B", "A"]


# ---- _rerank_with_retry ----
def test_rerank_with_retry_recovers_after_one_rate_limit(monkeypatch):
    """First call is rate-limited, second succeeds — retried once, and the
    backoff wait is exercised without actually sleeping in the test."""
    service = _service()
    rate_limit_error = TooManyRequestsError(body={"message": "rate limited"})
    service.rerank_engine = MagicMock()
    service.rerank_engine.rerank.side_effect = [rate_limit_error, [{"index": 0}]]
    sleep_calls = []
    monkeypatch.setattr("noc.service.time.sleep", lambda s: sleep_calls.append(s))

    result = service._rerank_with_retry(["doc"], "query")

    assert result == [{"index": 0}]
    assert service.rerank_engine.rerank.call_count == 2
    assert len(sleep_calls) == 1


def test_rerank_with_retry_raises_after_exhausting_attempts(monkeypatch):
    service = _service()
    rate_limit_error = TooManyRequestsError(body={"message": "rate limited"})
    service.rerank_engine = MagicMock()
    service.rerank_engine.rerank.side_effect = rate_limit_error
    monkeypatch.setattr("noc.service.time.sleep", lambda s: None)

    with pytest.raises(TooManyRequestsError):
        service._rerank_with_retry(["doc"], "query")

    assert service.rerank_engine.rerank.call_count == 2


# ---- get_one_by_noc_code ----
def test_get_one_by_noc_code_found_and_not_found():
    repo = MagicMock()
    repo.get_one_by_noc_code.return_value = NOC(noc_code="A")
    service = _service(repo)
    assert service.get_one_by_noc_code("A").noc_code == "A"

    repo.get_one_by_noc_code.return_value = None
    with pytest.raises(ValueError):
        service.get_one_by_noc_code("missing")


# ---- _get_noc_code_list ----
def test_get_noc_code_list_raises_clear_error_when_file_missing():
    service = _service()
    with pytest.raises(FileNotFoundError, match="NOC code list file not found"):
        service._get_noc_code_list("does-not-exist.csv")


def test_get_noc_code_list_raises_clear_error_when_column_missing(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("some_other_column\nvalue\n")
    service = _service()
    with pytest.raises(ValueError, match="missing expected column"):
        service._get_noc_code_list(str(csv_path))


# ---- _parse_noc ----
def test_parse_noc_raises_clear_error_when_title_missing():
    service = _service()
    with pytest.raises(ValueError, match="Could not find NOC title"):
        service._parse_noc("<html><body>no title here</body></html>")


def test_parse_noc_raises_clear_error_when_breakdown_summary_missing():
    service = _service()
    html = "<html><body><h2>21232 – Software engineers</h2><p>desc</p></body></html>"
    with pytest.raises(ValueError, match="missing 'TEER'"):
        service._parse_noc(html)


# ---- _fetch_and_parse_noc ----
def test_fetch_and_parse_noc_retries_transient_failure_then_succeeds(monkeypatch):
    import requests

    service = _service()
    monkeypatch.setattr("noc.service.time.sleep", lambda seconds: None)

    good_profile = NOC(noc_code="22222")
    call_count = 0

    def flaky_get(url, timeout=None):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise requests.RequestException("boom")
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.text = "<html>ok</html>"
        return response

    monkeypatch.setattr("noc.service.requests.get", flaky_get)
    monkeypatch.setattr(service, "_parse_noc", MagicMock(return_value=good_profile))

    result = service._fetch_and_parse_noc("22222", 0)

    assert result is good_profile
    assert call_count == 3


def test_fetch_and_parse_noc_raises_after_exhausting_retries(monkeypatch):
    import requests

    service = _service()
    monkeypatch.setattr("noc.service.time.sleep", lambda seconds: None)
    get_mock = MagicMock(side_effect=requests.RequestException("boom"))
    monkeypatch.setattr("noc.service.requests.get", get_mock)

    with pytest.raises(requests.RequestException, match="boom"):
        service._fetch_and_parse_noc("11111", 0)

    assert get_mock.call_count == 3


# ---- init_noc_info ----
def test_init_noc_info_skips_failed_codes_and_saves_the_rest(monkeypatch):
    import pandas as pd
    import requests

    repo = MagicMock()
    service = _service(repo)
    monkeypatch.setattr("noc.service.time.sleep", lambda seconds: None)
    monkeypatch.setattr(
        service, "_get_noc_code_list", MagicMock(return_value=["11111", "22222"])
    )

    good_profile = NOC(noc_code="22222")

    def fake_get(url, timeout=None):
        response = MagicMock()
        if "11111" in url:
            raise requests.RequestException("boom")
        response.raise_for_status.return_value = None
        response.text = "<html>ok</html>"
        return response

    monkeypatch.setattr("noc.service.requests.get", fake_get)
    monkeypatch.setattr(service, "_parse_noc", MagicMock(return_value=good_profile))

    service.init_noc_info("dummy.csv")

    repo.save_all.assert_called_once_with([good_profile])


def test_init_noc_info_raises_when_every_code_fails(monkeypatch):
    import requests

    repo = MagicMock()
    service = _service(repo)
    monkeypatch.setattr("noc.service.time.sleep", lambda seconds: None)
    monkeypatch.setattr(
        service, "_get_noc_code_list", MagicMock(return_value=["11111"])
    )
    monkeypatch.setattr(
        "noc.service.requests.get",
        MagicMock(side_effect=requests.RequestException("boom")),
    )

    with pytest.raises(RuntimeError, match="No NOC profiles"):
        service.init_noc_info("dummy.csv")

    repo.save_all.assert_not_called()


# ---- get_ideal_pool_count ----
def test_get_ideal_pool_count_delegates_to_repository():
    repo = MagicMock()
    repo.get_ideal_pool_count.return_value = (2, 3)
    service = _service(repo)
    ideal = IdealNOC(noc_code="A", minor_group_code="1", major_group_code="1")
    assert service.get_ideal_pool_count(ideal) == (2, 3)
    repo.get_ideal_pool_count.assert_called_once_with(ideal)
