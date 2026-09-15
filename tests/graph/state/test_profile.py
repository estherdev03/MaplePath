"""Tests for graph.state.profile Pydantic models."""

import pytest
from pydantic import ValidationError

from graph.state.profile import (
    CLBScore,
    CRSBreakdown,
    EducationLevel,
    EnglishTest,
    FrenchTest,
    MaritalStatus,
    NCLCScore,
    ProfileConfirmFormPayload,
    ProfileDraft,
)


def test_enum_values():
    assert {e.value for e in EducationLevel} == {
        "secondary",
        "one_year",
        "two_year",
        "bachelor",
        "two_or_more_credentials",
        "masters",
        "phd",
    }
    assert {e.value for e in EnglishTest} == {"ielts", "celpip", "pte", "tef", "tcf"}
    assert {e.value for e in FrenchTest} == {"tef", "tcf"}
    assert {e.value for e in MaritalStatus} == {"single", "married"}


def test_clb_score_and_nclc_score_require_all_four_skills():
    """Unlike LanguageScore, CLBScore/NCLCScore have no field defaults --
    every skill is required."""
    with pytest.raises(ValidationError):
        CLBScore(speaking=5, writing=5, listening=5)  # missing reading

    score = NCLCScore(speaking=5, writing=5, listening=5, reading=5)
    assert score.reading == 5


def test_crs_breakdown_defaults_to_zero_for_all_fields():
    """CRSService.calculate_crs relies on sum(breakdown.model_dump().values())
    starting from well-defined defaults."""
    assert all(v == 0 for v in CRSBreakdown().model_dump().values())


def test_profile_draft_missing_fields_and_warnings_default_to_empty_list():
    draft = ProfileDraft()
    assert draft.missing_fields == []
    assert draft.warnings == []


def test_profile_confirm_form_payload_required_vs_optional_fields():
    with pytest.raises(ValidationError):
        ProfileConfirmFormPayload()  # age and the rest are required
