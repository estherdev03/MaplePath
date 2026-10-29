"""Tests for crs.transferability.TransferabilityService."""

from crs.constants import FOREIGN_CAN_EXP
from graph.state.profile import (
    CLBScore,
    Education,
    EducationLevel,
    EnglishScore,
    EnglishTest,
    Experience,
    FrenchScore,
    FrenchTest,
    LanguageScore,
    Languages,
    NCLCScore,
)
from graph.state.shared import UserProfile

EDUCATION_LEVEL_LOW_HIGH = {
    EducationLevel.SECONDARY: (0, 0),
    EducationLevel.ONE_YEAR: (13, 25),
    EducationLevel.TWO_YEAR: (13, 25),
    EducationLevel.BACHELOR: (13, 25),
    EducationLevel.TWO_OR_MORE: (25, 50),
    EducationLevel.MASTERS: (25, 50),
    EducationLevel.PHD: (25, 50),
}

FOREIGN_EXP_LANGUAGE_LOW_HIGH = {
    0: (0, 0),
    1: (13, 25),
    2: (13, 25),
    3: (25, 50),
}


def _clb_english_profile(*skill_scores: int) -> UserProfile:
    """A UserProfile whose first (and only) language is English, with
    clb_scores already populated (skipping the lazy english_to_clb fill)."""
    speaking, writing, listening, reading = skill_scores
    return UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                is_first_language=True,
                clb_scores=CLBScore(
                    speaking=speaking,
                    writing=writing,
                    listening=listening,
                    reading=reading,
                ),
            ),
            french=None,
        )
    )


def _all_clb_profile(level: int) -> UserProfile:
    return _clb_english_profile(level, level, level, level)


# =========== _language_range ===========
def test_language_range_english_first_language(transferability_service):
    """Returns (all_clb5+, all_clb7+, all_clb9+) computed from CLB scores;
    also verify it lazily fills clb_scores when missing."""
    score = LanguageScore(speaking=7.0, writing=7.0, listening=8.0, reading=7.0)
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS, detail_scores=score, is_first_language=True
            ),
            french=None,
        )
    )
    assert profile.languages.english.clb_scores is None

    result = transferability_service._language_range(profile)

    assert result == (True, True, True)
    assert profile.languages.english.clb_scores == CLBScore(
        speaking=9, writing=9, listening=9, reading=9
    )


def test_language_range_french_first_language(transferability_service):
    """Same as above but sourced from NCLC scores."""
    score = LanguageScore(speaking=380, writing=380, listening=300, reading=250)
    profile = UserProfile(
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TEF, detail_scores=score, is_first_language=True
            ),
            english=None,
        )
    )
    assert profile.languages.french.nclc_scores is None

    result = transferability_service._language_range(profile)

    assert result == (True, True, True)
    assert profile.languages.french.nclc_scores == NCLCScore(
        speaking=9, writing=9, listening=9, reading=9
    )


def test_language_range_no_first_language_returns_all_false(transferability_service):
    """No languages, or neither marked is_first_language -> (False, False, False).

    Note: Languages.validate_languages auto-sets is_first_language=True when
    only one language is given, and requires exactly one is_first_language
    when both are given -> so "neither marked first" can't actually be
    constructed. Only the "no languages" path is exercised here.
    """
    profile = UserProfile(languages=None)
    assert transferability_service._language_range(profile) == (False, False, False)


# =========== education_language_points_calc ===========
def test_education_language_points_invalid_education_returns_zero(
    transferability_service,
):
    """not from_canada and not eca_completed -> 0."""
    profile = _all_clb_profile(9)
    profile.education = Education(
        level=EducationLevel.BACHELOR, from_canada=False, eca_completed=False
    )
    assert transferability_service.education_language_points_calc(profile) == 0


def test_education_language_points_clb9_uses_high_tier_per_level(
    transferability_service,
):
    """Each EducationLevel with all_clb9 -> EDUCATION_LANGUAGE[level][1]."""
    profile = _all_clb_profile(9)
    for level, (_, high) in EDUCATION_LEVEL_LOW_HIGH.items():
        profile.education = Education(level=level, from_canada=True)
        assert transferability_service.education_language_points_calc(profile) == high


def test_education_language_points_clb7_uses_low_tier_per_level(
    transferability_service,
):
    """Each EducationLevel with all_clb7 (not clb9) -> EDUCATION_LANGUAGE[level][0]."""
    profile = _all_clb_profile(7)
    for level, (low, _) in EDUCATION_LEVEL_LOW_HIGH.items():
        profile.education = Education(level=level, from_canada=True)
        assert transferability_service.education_language_points_calc(profile) == low


def test_education_language_points_below_clb7_returns_zero(transferability_service):
    profile = _all_clb_profile(6)
    for level, _ in EDUCATION_LEVEL_LOW_HIGH.items():
        profile.education = Education(level=level, from_canada=True)
        assert transferability_service.education_language_points_calc(profile) == 0


# =========== education_can_exp_points_calc ===========
def test_education_can_exp_points_no_work_experience_returns_zero(
    transferability_service,
):
    profile = UserProfile(
        education=Education(level=EducationLevel.BACHELOR, from_canada=True)
    )
    assert transferability_service.education_can_exp_points_calc(profile) == 0

    profile.work_experience = Experience(canada_years=0)
    assert transferability_service.education_can_exp_points_calc(profile) == 0


def test_education_can_exp_points_invalid_education_returns_zero(
    transferability_service,
):
    """Missing education, not from_canada/eca_completed, or missing level -> 0."""
    profile = UserProfile(work_experience=Experience(canada_years=2))

    # missing education entirely
    assert transferability_service.education_can_exp_points_calc(profile) == 0

    # education present but neither from_canada nor eca_completed
    profile.education = Education(
        level=EducationLevel.BACHELOR, from_canada=False, eca_completed=False
    )
    assert transferability_service.education_can_exp_points_calc(profile) == 0


def test_education_can_exp_points_one_year_uses_low_tier_per_level(
    transferability_service,
):
    """canada_years == 1 -> EDUCATION_CAN_EXP[level][0]."""
    profile = UserProfile(work_experience=Experience(canada_years=1))
    for level, (low, _) in EDUCATION_LEVEL_LOW_HIGH.items():
        profile.education = Education(level=level, from_canada=True)
        assert transferability_service.education_can_exp_points_calc(profile) == low


def test_education_can_exp_points_more_than_one_year_uses_high_tier_per_level(
    transferability_service,
):
    """canada_years > 1 -> EDUCATION_CAN_EXP[level][1]."""
    profile = UserProfile(work_experience=Experience(canada_years=2))
    for level, (_, high) in EDUCATION_LEVEL_LOW_HIGH.items():
        profile.education = Education(level=level, from_canada=True)
        assert transferability_service.education_can_exp_points_calc(profile) == high


# =========== foreign_exp_lang_points_calc ===========
def test_foreign_exp_lang_points_no_foreign_experience_returns_zero(
    transferability_service,
):
    profile = _all_clb_profile(9)
    assert transferability_service.foreign_exp_lang_points_calc(profile) == 0

    profile.work_experience = Experience(foreign_years=0)
    assert transferability_service.foreign_exp_lang_points_calc(profile) == 0


def test_foreign_exp_lang_points_years_capped_at_three(transferability_service):
    """foreign_years of 3 or greater are all resolve to the yoe=3 bucket."""
    profile_low = _all_clb_profile(7)
    profile_high = _all_clb_profile(9)

    # yoe >= 3
    for years in (3, 4, 5):
        profile_low.work_experience = Experience(foreign_years=years)
        profile_high.work_experience = Experience(foreign_years=years)
        result_low = transferability_service.foreign_exp_lang_points_calc(profile_low)
        result_high = transferability_service.foreign_exp_lang_points_calc(profile_high)
        # yoe capped at 3
        assert result_low == FOREIGN_EXP_LANGUAGE_LOW_HIGH[3][0]
        assert result_high == FOREIGN_EXP_LANGUAGE_LOW_HIGH[3][1]


def test_foreign_exp_lang_points_clb9_vs_clb7_vs_below(transferability_service):
    """FOREIGN_EXP_LANGUAGE[yoe][1] for clb9, [yoe][0] for clb7, else 0."""
    work_experience = Experience(foreign_years=1)

    profile9 = _all_clb_profile(9)
    profile9.work_experience = work_experience
    assert (
        transferability_service.foreign_exp_lang_points_calc(profile9)
        == FOREIGN_EXP_LANGUAGE_LOW_HIGH[1][1]
    )

    profile7 = _all_clb_profile(7)
    profile7.work_experience = work_experience
    assert (
        transferability_service.foreign_exp_lang_points_calc(profile7)
        == FOREIGN_EXP_LANGUAGE_LOW_HIGH[1][0]
    )

    profile6 = _all_clb_profile(6)
    profile6.work_experience = work_experience
    assert transferability_service.foreign_exp_lang_points_calc(profile6) == 0


# =========== foreign_can_exp_points_calc ===========
def test_foreign_can_exp_points_missing_or_zero_canada_years_returns_zero(
    transferability_service,
):
    """No work_experience, canada_years falsy, or canada_years <= 0 -> 0."""
    profile = UserProfile(work_experience=None)
    assert transferability_service.foreign_can_exp_points_calc(profile) == 0

    profile.work_experience = Experience(canada_years=0, foreign_years=2)
    assert transferability_service.foreign_can_exp_points_calc(profile) == 0


def test_foreign_can_exp_points_missing_foreign_years_returns_zero(
    transferability_service,
):
    profile = UserProfile(work_experience=Experience(canada_years=2, foreign_years=0))
    assert transferability_service.foreign_can_exp_points_calc(profile) == 0


def test_foreign_can_exp_points_axes_capped_at_two_and_three(transferability_service):
    """canada_years capped at 2, foreign_years capped at 3 before lookup."""
    profile = UserProfile(work_experience=Experience(canada_years=5, foreign_years=10))
    assert transferability_service.foreign_can_exp_points_calc(profile) == 50


# =========== trade_lang_points_calc ===========
def test_trade_lang_points_no_coq_returns_zero(transferability_service):
    """No education, or has_COQ falsy -> 0."""
    profile = _all_clb_profile(9)
    assert transferability_service.trade_lang_points_calc(profile) == 0

    profile.education = Education(level=EducationLevel.BACHELOR, has_COQ=False)
    assert transferability_service.trade_lang_points_calc(profile) == 0


def test_trade_lang_points_coq_with_clb7_returns_50(transferability_service):
    profile = _all_clb_profile(7)
    profile.education = Education(level=EducationLevel.BACHELOR, has_COQ=True)
    assert transferability_service.trade_lang_points_calc(profile) == 50


def test_trade_lang_points_coq_with_clb5_returns_25(transferability_service):
    profile = _all_clb_profile(5)
    profile.education = Education(level=EducationLevel.BACHELOR, has_COQ=True)
    assert transferability_service.trade_lang_points_calc(profile) == 25


def test_trade_lang_points_coq_below_clb5_returns_zero(transferability_service):
    profile = _all_clb_profile(4)
    profile.education = Education(level=EducationLevel.BACHELOR, has_COQ=True)
    assert transferability_service.trade_lang_points_calc(profile) == 0
