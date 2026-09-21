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


def test_parse_profile_builds_profile_draft_event_and_returns_result():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.return_value = {"profile": {"age": 30}}
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 200
    assert response.json() == {"result": {"age": 30}}
    called_state = mock_graph.invoke.call_args[0][0]
    assert called_state["event"].event_type == "profile_draft"
    assert called_state["event"].payload.text == "hello"


def test_complete_profile_builds_profile_confirm_event_and_returns_result():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.return_value = {"profile": {"age": 30}}
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 200
    assert response.json() == {"result": {"age": 30}}
    called_state = mock_graph.invoke.call_args[0][0]
    assert called_state["event"].event_type == "profile_confirm"
    assert called_state["event"].payload.job_title == "Software Engineer"


def test_complete_profile_invalid_body_returns_422():
    response = client.post("/profile/complete", json={})
    assert response.status_code == 422


def test_parse_profile_value_error_returns_400():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = ValueError("No matching NOC occupation found")
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 400
    assert response.json() == {"detail": "No matching NOC occupation found"}


def test_parse_profile_unexpected_error_returns_500_without_leaking_details():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = RuntimeError("db connection refused")
        response = client.post("/profile/parse", params={"profile_text": "hello"})

    assert response.status_code == 500
    assert "db connection refused" not in response.text


def test_complete_profile_value_error_returns_400():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = ValueError("Spouse information is required")
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 400
    assert response.json() == {"detail": "Spouse information is required"}


def test_complete_profile_rate_limited_returns_429_with_actionable_detail():
    with patch("api.app.compiled_graph") as mock_graph:
        mock_graph.invoke.side_effect = TooManyRequestsError(body={"message": "rate limited"})
        response = client.post("/profile/complete", json=_confirm_payload_json())

    assert response.status_code == 429
    assert "try again" in response.json()["detail"].lower()


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


def test_simulate_crs_returns_score_and_eligibility():
    with (
        patch("api.app.crs_service") as mock_crs_service,
        patch("api.app.eligibility_service") as mock_eligibility_service,
    ):
        mock_crs_service.calculate_crs.return_value = "crs-result"
        mock_eligibility_service.evaluate_express_entry.return_value = "eligibility-result"
        response = client.post("/crs/simulate", json=_minimal_user_profile_json())

    assert response.status_code == 200
    assert response.json() == {
        "crs_score": "crs-result",
        "eligibility": "eligibility-result",
    }


def test_simulate_crs_invalid_body_returns_422():
    response = client.post("/crs/simulate", json={"age": "not-a-number"})
    assert response.status_code == 422


def test_simulate_crs_unexpected_error_returns_500_without_leaking_details():
    with patch("api.app.crs_service") as mock_crs_service:
        mock_crs_service.calculate_crs.side_effect = RuntimeError("db connection refused")
        response = client.post("/crs/simulate", json=_minimal_user_profile_json())

    assert response.status_code == 500
    assert "db connection refused" not in response.text


def test_noc_retrieval_evaluate_missing_file_returns_500():
    with patch(
        "api.app.noc_retrieval_method_evaluate",
        side_effect=FileNotFoundError("data/noc_eval_labels.csv"),
    ):
        response = client.get("/evaluate")

    assert response.status_code == 500


def test_noc_retrieval_evaluate_rate_limited_returns_429_with_actionable_detail():
    with patch(
        "api.app.noc_retrieval_method_evaluate",
        side_effect=TooManyRequestsError(body={"message": "rate limited"}),
    ):
        response = client.get("/evaluate")

    assert response.status_code == 429
    assert "try again" in response.json()["detail"].lower()


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
