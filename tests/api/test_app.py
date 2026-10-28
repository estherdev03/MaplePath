"""Tests for api.app FastAPI endpoints."""

from unittest.mock import patch

from cohere.errors import TooManyRequestsError
from fastapi.testclient import TestClient

from api.app import app
from graph.state.profile import (
    CanadaEducation,
    Education,
    EducationLevel,
    EnglishScore,
    EnglishTest,
    Experience,
    Languages,
    MaritalStatus,
    ProfileConfirmFormPayload,
    SpouseProfile,
)
from noc.types import (
    CompleteExamplesReport,
    RetrievalMethodMeanReport,
    SingleExampleReport,
)

client = TestClient(app)


def _confirm_payload_json():
    payload = ProfileConfirmFormPayload(
        age=30,
        job_title="Software Engineer",
        job_responsibility="Build web apps",
        have_canada_job_offer=False,
        languages=Languages(
            english=EnglishScore(test_name=EnglishTest.IELTS, is_first_language=True),
            french=None,
        ),
        work_experience=Experience(),
        marital_status=MaritalStatus.SINGLE,
        education=Education(level=EducationLevel.BACHELOR),
        canada_education=CanadaEducation(completed=False, credential_years=0),
        provincial_nomination=False,
        sibling_in_can=False,
        relative_in_can=False,
        spouse=SpouseProfile(),
        current_available_funds=1000,
    )
    return payload.model_dump(mode="json")


# ===================  Test /profile/parse ===================
# Test return result and event of /profile/parse route
def test_parse_profile_builds_profile_draft_event_and_returns_result():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.return_value = {"profile": {"age": 30}}
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 200
    assert response.json() == {"result": {"age": 30}}
    called_state = mock_graph.invoke.call_args[0][0]
    assert called_state["event"].event_type == "profile_draft"
    assert called_state["event"].payload.text == "hello"


# Test 400 error of /profile/parse
def test_parse_profile_value_error_returns_400():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = ValueError("No matching NOC occupation found")
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 400
    assert response.json() == {"detail": "No matching NOC occupation found"}


# Test 500 error of /profile/parse
def test_parse_profile_unexpected_error_returns_500_without_leaking_details():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = RuntimeError("db connection refused")
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 500
    assert "db connection refused" not in response.text
    assert response.json() == {"detail": "Failed to parse profile"}


# ===================  Test /profile/complete ===================
# Test return result and event of /profile/complete route
def test_complete_profile_builds_profile_confirm_event_and_returns_result():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.return_value = {"profile": {"age": 30}}
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 200
    assert response.json() == {"result": {"age": 30}}
    called_state = mock_graph.invoke.call_args[0][0]
    assert called_state["event"].event_type == "profile_confirm"
    assert called_state["event"].payload.job_title == "Software Engineer"


# Test invalid body return 422 from /profile/complete
def test_complete_profile_invalid_body_returns_422():
    response = client.post("/profile/complete", json={})
    assert response.status_code == 422


# Test 400 error of /profile/complete
def test_complete_profile_value_error_returns_400():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = ValueError("Spouse information is required")
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 400
    assert response.json() == {"detail": "Spouse information is required"}


# Test 429 error of /profile/complete
def test_complete_profile_rate_limited_returns_429_with_actionable_detail():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = TooManyRequestsError(
            body={"message": "rate limited"}
        )
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 429
    assert response.json() == {
        "detail": "The occupation classifier's search service is rate-limited right now. Please try again in about a minute."
    }


def test_complete_profile_unexpected_error_return_500():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = RuntimeError("db connection refused")
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to complete profile"}


# =================== Test /crs/simulate ===================
def _minimal_user_profile_json():
    return {
        "age": 30,
        "occupation": {"title": "Software Engineer", "noc_code": "21232", "teer": 1},
        "languages": {
            "english": {"test_name": "ielts", "is_first_language": True},
            "french": None,
        },
        "work_experience": {},
        "marital_status": "single",
        "education": {"level": "bachelor"},
        "canada_education": {"completed": False, "credential_years": 0},
        "current_available_funds": 1000,
    }


# Test simulate_crs return
def test_simulate_crs_returns_score_and_eligibility():
    with (
        patch("api.app.crs_service") as mock_crs_service,
        patch("api.app.eligibility_service") as mock_eligibility_service,
    ):
        mock_crs_service.calculate_crs.return_value = "crs-result"
        mock_eligibility_service.evaluate_express_entry.return_value = (
            "eligibility-result"
        )
        response = client.post("/crs/simulate", json=_minimal_user_profile_json())

    assert response.status_code == 200
    assert response.json() == {
        "crs_score": "crs-result",
        "eligibility": "eligibility-result",
    }


# Test 422 error from simulate_crs
def test_simulate_crs_invalid_body_returns_422():
    response = client.post("/crs/simulate", json={"age": "not-a-number"})
    assert response.status_code == 422


# Test 400 error from simulate_crs
def test_simulate_crs_value_error_returns_400():
    with patch("api.app.crs_service") as mock_crs_service:
        mock_crs_service.calculate_crs.side_effect = ValueError("invalid value")
        response = client.post("/crs/simulate", json=_minimal_user_profile_json())
    assert response.status_code == 400
    assert response.json() == {"detail": "invalid value"}


# Test 500 error from simulate_crs
def test_simulate_crs_unexpected_error_returns_500_without_leaking_details():
    with patch("api.app.crs_service") as mock_crs_service:
        mock_crs_service.calculate_crs.side_effect = RuntimeError(
            "db connection refused"
        )
        response = client.post("/crs/simulate", json=_minimal_user_profile_json())

    assert response.status_code == 500
    assert "db connection refused" not in response.text


# Test missing field when calling /crs/simulate
def test_simulate_crs_empty_profile_returns_422_listing_missing_fields():
    with patch("api.app.crs_service") as mock_crs_service:
        response = client.post("/crs/simulate", json={})

    assert response.status_code == 422
    detail = response.json()["detail"]
    for field in ("age", "occupation", "languages", "education"):
        assert field in detail
    mock_crs_service.calculate_crs.assert_not_called()


# Test missing spouse profle in /crs/simulate
def test_simulate_crs_married_without_spouse_returns_422():
    profile = _minimal_user_profile_json() | {"marital_status": "married"}
    response = client.post("/crs/simulate", json=profile)

    assert response.status_code == 422
    assert "spouse" in response.json()["detail"]


# =================== Test /evaluate ===================
# Test missing file 500 error
def test_noc_retrieval_evaluate_missing_file_returns_500():
    with patch(
        "api.app.noc_retrieval_method_evaluate",
        side_effect=FileNotFoundError("data/noc_eval_labels.csv"),
    ):
        response = client.get("/evaluate")

    assert response.status_code == 500


# Test rate limited 429 error
def test_noc_retrieval_evaluate_rate_limited_returns_429_with_actionable_detail():
    with patch(
        "api.app.noc_retrieval_method_evaluate",
        side_effect=TooManyRequestsError(body={"message": "rate limited"}),
    ):
        response = client.get("/evaluate")

    assert response.status_code == 429
    assert "try again" in response.json()["detail"].lower()


# Test examples and mean report
def test_noc_retrieval_evaluate_returns_examples_and_mean_report():
    single = SingleExampleReport(
        case_type="core",
        job_title="Engineer",
        bm25=(0.5, 1),
        vector=(0.6, 1),
        rrf=(0.7, 1),
        hybrid=(0.8, 1),
    )
    examples = CompleteExamplesReport(report=[single])
    mean = RetrievalMethodMeanReport(
        bm25=(0.5, 1), vector=(0.6, 1), rrf=(0.7, 1), hybrid=(0.8, 1)
    )

    with patch(
        "api.app.noc_retrieval_method_evaluate", return_value=(examples, mean)
    ) as mock_eval:
        response = client.get("/evaluate")

    assert response.status_code == 200
    body = response.json()
    assert body["mean_report"]["bm25"] == [0.5, 1]
    assert body["examples_report"][0]["job_title"] == "Engineer"
    mock_eval.assert_called_once_with("data/noc_eval_labels.csv")


def test_noc_retrieval_evaluate_returns_500_unexpected_error():
    with patch(
        "api.app.noc_retrieval_method_evaluate",
        side_effect=RuntimeError("runtime error"),
    ):
        response = client.get("/evaluate")

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to run NOC retrieval evaluation"}


# =================== Test API key  ===================
# Test request allowed without API key
def test_requests_allowed_without_key_when_api_key_unset(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.return_value = {"profile": {"age": 30}}
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 200


# Test missing API key when API key is set
def test_missing_api_key_returns_401_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    with patch("api.app.compiled_graph") as mock_graph:
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 401
    mock_graph.invoke.assert_not_called()


# Test wrong API key when API key is set
def test_wrong_api_key_returns_401_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    response = client.get("/evaluate", headers={"X-API-Key": "wrong"})

    assert response.status_code == 401


# Test correct API key
def test_correct_api_key_is_accepted_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.return_value = {"profile": {"age": 30}}
        response = client.post(
            "/profile/parse",
            params={"profile_text": "hello"},
            headers={"X-API-Key": "secret"},
        )

    assert response.status_code == 200
