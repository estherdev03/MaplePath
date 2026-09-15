"""Tests for user_profile.service.ProfileService."""

from unittest.mock import MagicMock


from graph.state.profile import (
    CanadaEducation,
    Education,
    EducationLevel,
    EnglishScore,
    EnglishTest,
    Experience,
    Languages,
    MaritalStatus,
    Occupation,
    ProfileConfirmFormPayload,
    SpouseProfile,
)
import pytest

from user_profile.service import ProfileService
from user_profile.types import LLMNocResult, NOCResult


def _service():
    return ProfileService(
        noc_service=MagicMock(),
        crs_service=MagicMock(),
        eligibility_service=MagicMock(),
    )


def _payload():
    return ProfileConfirmFormPayload(
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


# ---- create ----
def test_create_maps_payload_and_resolved_occupation_into_user_profile(monkeypatch):
    """Mock _get_occupation; assert UserProfile fields are populated from
    the ProfileConfirmFormPayload."""
    service = _service()
    fake_occupation = Occupation(title="Software Engineer", noc_code="21232")
    monkeypatch.setattr(
        service, "_get_occupation", MagicMock(return_value=fake_occupation)
    )
    payload = _payload()

    user = service.create(payload)

    service._get_occupation.assert_called_once_with(
        payload.job_title, payload.job_responsibility, payload.have_canada_job_offer
    )
    assert user.age == 30
    assert user.occupation == fake_occupation
    assert user.languages is payload.languages
    assert user.marital_status == MaritalStatus.SINGLE
    assert user.current_available_funds == 1000


# ---- _get_occupation ----
def test_get_occupation_builds_occupation_from_noc_result(monkeypatch):
    """Mock _parse_NOC; assert Occupation fields (incl.
    have_canada_job_offer passthrough) map from NOCResult."""
    service = _service()
    noc_result = NOCResult(
        title="Software Engineer",
        noc_code="21232",
        teer=1,
        major_group_code="21",
        minor_group_code="2123",
        submajor_group_code="212",
        noc_confidence=0.9,
    )
    monkeypatch.setattr(service, "_parse_NOC", MagicMock(return_value=noc_result))

    occupation = service._get_occupation("Software Engineer", "Build apps", True)

    assert occupation.title == "Software Engineer"
    assert occupation.noc_code == "21232"
    assert occupation.teer == 1
    assert occupation.have_canada_job_offer is True
    assert occupation.noc_confidence == 0.9


# ---- _parse_NOC ----
def test_parse_nocs_raises_clear_error_when_llm_finds_no_match(monkeypatch):
    """When the LLM returns noc_code=None (no confident candidate match),
    raise a clear ValueError instead of calling get_one_by_noc_code(None)."""
    fake_structured_llm = MagicMock()
    fake_structured_llm.invoke.return_value = LLMNocResult(
        noc_code=None,
        reasoning="None of the provided candidates sufficiently match.",
    )
    fake_llm = MagicMock()
    fake_llm.with_structured_output.return_value = fake_structured_llm
    monkeypatch.setattr(
        "user_profile.service.init_chat_model", MagicMock(return_value=fake_llm)
    )
    service = _service()
    service.noc_service.noc_hybrid_search.return_value = []

    with pytest.raises(ValueError, match="Software Engineer"):
        service._parse_NOC(
            job_title="Software Engineer", job_responsibility="Build web apps"
        )

    service.noc_service.get_one_by_noc_code.assert_not_called()


# ---- calculate_CRS ----
def test_calculate_crs_sets_user_crs_score_and_returns_same_profile():
    """Mock crs_service.calculate_crs."""
    crs_service = MagicMock()
    crs_service.calculate_crs.return_value = "crs-result"
    service = ProfileService(
        noc_service=MagicMock(),
        crs_service=crs_service,
        eligibility_service=MagicMock(),
    )
    user = MagicMock()

    result = service.calculate_CRS(user)

    assert result is user
    assert user.crs_score == "crs-result"


# ---- evaluate_express_entry ----
def test_evaluate_express_entry_sets_user_eligibility_and_returns_same_profile():
    """Mock eligibility_service.evaluate_express_entry."""
    eligibility_service = MagicMock()
    eligibility_service.evaluate_express_entry.return_value = "eligibility-result"
    service = ProfileService(
        noc_service=MagicMock(),
        crs_service=MagicMock(),
        eligibility_service=eligibility_service,
    )
    user = MagicMock()

    result = service.evaluate_express_entry(user)

    assert result is user
    assert user.eligibility == "eligibility-result"


# ---- create_advice ----
def test_create_advice_sets_user_advice_from_llm_response_content(monkeypatch):
    """Mock init_chat_model().invoke; assert user.advice == response.content."""
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = MagicMock(content="Some advice")
    monkeypatch.setattr(
        "user_profile.service.init_chat_model", MagicMock(return_value=fake_llm)
    )
    service = _service()
    user = MagicMock()

    result = service.create_advice(user)

    assert result is user
    assert user.advice == "Some advice"
