"""Tests for crs.service.CRSService."""

import pytest

from graph.state.profile import (
    CanadaEducation,
    Education,
    EducationLevel,
    EnglishScore,
    EnglishTest,
    Experience,
    FrenchScore,
    FrenchTest,
    LanguageScore,
    Languages,
    MaritalStatus,
    SpouseProfile,
)
from graph.state.shared import UserProfile


# ---- _age_points ----
def test_age_points_below_18_returns_zero(crs_service):
    assert crs_service._age_points(UserProfile(age=17)) == 0
    assert crs_service._age_points(UserProfile(age=None)) == 0


def test_age_points_45_and_above_returns_zero(crs_service):
    assert crs_service._age_points(UserProfile(age=45)) == 0
    assert crs_service._age_points(UserProfile(age=60)) == 0


def test_age_points_single_table_18_to_44(crs_service):
    """Spot-check a few ages against AGE_POINTS_SINGLE."""
    assert crs_service._age_points(UserProfile(age=18)) == 99
    assert crs_service._age_points(UserProfile(age=29)) == 110
    assert crs_service._age_points(UserProfile(age=35)) == 77
    assert crs_service._age_points(UserProfile(age=44)) == 6


def test_age_points_married_table_18_to_44(crs_service):
    """Spot-check a few ages against AGE_POINTS_MARRIED."""
    married = MaritalStatus.MARRIED
    assert crs_service._age_points(UserProfile(age=18, marital_status=married)) == 90
    assert crs_service._age_points(UserProfile(age=29, marital_status=married)) == 100
    assert crs_service._age_points(UserProfile(age=35, marital_status=married)) == 70
    assert crs_service._age_points(UserProfile(age=44, marital_status=married)) == 5


# ---- _education_points ----
def test_education_points_no_education_returns_zero(crs_service):
    assert crs_service._education_points(UserProfile(education=None)) == 0


def test_education_points_not_from_canada_and_no_eca_returns_zero(crs_service):
    profile = UserProfile(
        education=Education(
            level=EducationLevel.BACHELOR, from_canada=False, eca_completed=False
        )
    )
    assert crs_service._education_points(profile) == 0


def test_education_points_single_vs_married_tables(crs_service):
    single = UserProfile(
        education=Education(level=EducationLevel.PHD, from_canada=True)
    )
    married = UserProfile(
        education=Education(level=EducationLevel.PHD, from_canada=True),
        marital_status=MaritalStatus.MARRIED,
    )
    assert crs_service._education_points(single) == 150
    assert crs_service._education_points(married) == 140


# ---- _first/_second_language_points ----
def test_first_language_points_english_first_language(crs_service):
    """Also asserts profile.languages.english.clb_scores gets populated."""
    score = LanguageScore(
        speaking=7.5, writing=7.5, listening=8.5, reading=8.0
    )  # CLB10
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS, detail_scores=score, is_first_language=True
            ),
            french=None,
        )
    )
    result = crs_service._first_language_points(profile)
    assert profile.languages.english.clb_scores.model_dump() == {
        "speaking": 10,
        "writing": 10,
        "listening": 10,
        "reading": 10,
    }
    assert result == 34 * 4  # FIRST_LANGUAGE_SINGLE[10] per skill


def test_first_language_points_french_first_language(crs_service):
    """Also asserts profile.languages.french.nclc_scores gets populated."""
    score = LanguageScore(
        speaking=393, writing=393, listening=316, reading=263
    )  # NCLC10
    profile = UserProfile(
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TEF, detail_scores=score, is_first_language=True
            ),
            english=None,
        )
    )
    result = crs_service._first_language_points(profile)
    assert profile.languages.french.nclc_scores.model_dump() == {
        "speaking": 10,
        "writing": 10,
        "listening": 10,
        "reading": 10,
    }
    assert result == 34 * 4


def test_first_language_points_no_languages_returns_zero(crs_service):
    profile = UserProfile(languages=None)
    assert crs_service._first_language_points(profile) == 0


def test_second_language_points_english_second_language(crs_service):
    # IELTS scores chosen to all land on CLB 7.
    eng_score = LanguageScore(speaking=6.0, writing=6.0, listening=6.0, reading=6.0)
    fr_score = LanguageScore(speaking=393, writing=393, listening=316, reading=263)
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=eng_score,
                is_first_language=False,
            ),
            french=FrenchScore(
                test_name=FrenchTest.TEF, detail_scores=fr_score, is_first_language=True
            ),
        )
    )
    result = crs_service._second_language_points(profile)
    assert profile.languages.english.clb_scores.model_dump() == {
        "speaking": 7,
        "writing": 7,
        "listening": 7,
        "reading": 7,
    }
    assert result == 3 * 4  # SECOND_LANGUAGE[7] per skill


def test_second_language_points_french_second_language(crs_service):
    # TCF scores chosen to all land on NCLC 7.
    fr_score = LanguageScore(speaking=10, writing=10, listening=458, reading=453)
    eng_score = LanguageScore(speaking=7.5, writing=7.5, listening=8.5, reading=8.0)
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=eng_score,
                is_first_language=True,
            ),
            french=FrenchScore(
                test_name=FrenchTest.TCF,
                detail_scores=fr_score,
                is_first_language=False,
            ),
        )
    )
    result = crs_service._second_language_points(profile)
    assert profile.languages.french.nclc_scores.model_dump() == {
        "speaking": 7,
        "writing": 7,
        "listening": 7,
        "reading": 7,
    }
    assert result == 3 * 4


def test_second_language_points_no_second_language_returns_zero(crs_service):
    score = LanguageScore(speaking=7.5, writing=7.5, listening=8.5, reading=8.0)
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS, detail_scores=score, is_first_language=True
            ),
            french=None,
        )
    )
    assert crs_service._second_language_points(profile) == 0


# ---- _canadian_experience_points ----
def test_canadian_experience_points_no_experience_returns_zero(crs_service):
    """No work_experience, or canada_years < 1 -> 0."""
    assert (
        crs_service._canadian_experience_points(UserProfile(work_experience=None)) == 0
    )
    profile = UserProfile(work_experience=Experience(canada_years=0))
    assert crs_service._canadian_experience_points(profile) == 0


def test_canadian_experience_points_capped_at_five_years(crs_service):
    five = UserProfile(work_experience=Experience(canada_years=5))
    ten = UserProfile(work_experience=Experience(canada_years=10))
    assert crs_service._canadian_experience_points(five) == 80
    assert crs_service._canadian_experience_points(ten) == 80


def test_canadian_experience_points_single_vs_married_tables(crs_service):
    single = UserProfile(work_experience=Experience(canada_years=3))
    married = UserProfile(
        work_experience=Experience(canada_years=3), marital_status=MaritalStatus.MARRIED
    )
    assert crs_service._canadian_experience_points(single) == 64
    assert crs_service._canadian_experience_points(married) == 56


# ---- _spouse_points ----
def test_spouse_points_no_spouse_education_returns_zero_education_points(crs_service):
    profile = UserProfile(spouse=SpouseProfile(education=None))
    _, breakdown = crs_service._spouse_points(profile)
    assert breakdown.education == 0


def test_spouse_points_invalid_spouse_education_returns_zero(crs_service):
    """Not from_canada and not eca_completed -> 0 education points."""
    profile = UserProfile(
        spouse=SpouseProfile(
            education=Education(
                level=EducationLevel.BACHELOR, from_canada=False, eca_completed=False
            )
        )
    )
    _, breakdown = crs_service._spouse_points(profile)
    assert breakdown.education == 0


def test_spouse_points_english_language_scores(crs_service):
    score = LanguageScore(
        speaking=7.5, writing=7.5, listening=8.5, reading=8.0
    )  # CLB10
    profile = UserProfile(
        spouse=SpouseProfile(
            languages=Languages(
                english=EnglishScore(
                    test_name=EnglishTest.IELTS,
                    detail_scores=score,
                    is_first_language=True,
                ),
                french=None,
            )
        )
    )
    _, breakdown = crs_service._spouse_points(profile)
    assert profile.spouse.languages.english.clb_scores.model_dump() == {
        "speaking": 10,
        "writing": 10,
        "listening": 10,
        "reading": 10,
    }
    assert breakdown.language == 5 * 4  # SPOUSE_LANGUAGE_POINTS[10] per skill


def test_spouse_points_french_language_scores(crs_service):
    score = LanguageScore(
        speaking=393, writing=393, listening=316, reading=263
    )  # NCLC10
    profile = UserProfile(
        spouse=SpouseProfile(
            languages=Languages(
                french=FrenchScore(
                    test_name=FrenchTest.TEF,
                    detail_scores=score,
                    is_first_language=True,
                ),
                english=None,
            )
        )
    )
    _, breakdown = crs_service._spouse_points(profile)
    assert profile.spouse.languages.french.nclc_scores.model_dump() == {
        "speaking": 10,
        "writing": 10,
        "listening": 10,
        "reading": 10,
    }
    assert breakdown.language == 5 * 4


def test_spouse_points_missing_test_scores_returns_zero_language_points(crs_service):
    profile = UserProfile(
        spouse=SpouseProfile(
            languages=Languages(
                english=EnglishScore(
                    test_name=EnglishTest.IELTS,
                    detail_scores=None,
                    is_first_language=True,
                ),
                french=None,
            )
        )
    )
    _, breakdown = crs_service._spouse_points(profile)
    assert breakdown.language == 0


def test_spouse_points_canadian_experience_capped_at_five(crs_service):
    five = UserProfile(spouse=SpouseProfile(canadian_experience=5))
    ten = UserProfile(spouse=SpouseProfile(canadian_experience=10))
    _, breakdown_five = crs_service._spouse_points(five)
    _, breakdown_ten = crs_service._spouse_points(ten)
    assert breakdown_five.canadian_experience == 10  # SPOUSE_CANADIAN_EXPERIENCE[5]
    assert breakdown_ten.canadian_experience == 10


def test_spouse_points_returns_correct_total_and_breakdown(crs_service):
    """total == education + language + canadian_experience."""
    profile = UserProfile(
        spouse=SpouseProfile(
            education=Education(level=EducationLevel.BACHELOR, from_canada=True),
            languages=Languages(
                english=EnglishScore(
                    test_name=EnglishTest.IELTS,
                    detail_scores=LanguageScore(
                        speaking=7.5, writing=7.5, listening=8.5, reading=8.0
                    ),
                    is_first_language=True,
                ),
                french=None,
            ),
            canadian_experience=3,
        )
    )
    total, breakdown = crs_service._spouse_points(profile)
    assert breakdown.education == 8  # SPOUSE_EDUCATION[BACHELOR]
    assert breakdown.language == 20  # SPOUSE_LANGUAGE_POINTS[10] * 4
    assert breakdown.canadian_experience == 8  # SPOUSE_CANADIAN_EXPERIENCE[3]
    assert (
        total
        == breakdown.education + breakdown.language + breakdown.canadian_experience
    )


# ---- _skill_transferability_points ----
def test_skill_transferability_points_sums_all_five_components(crs_service):
    score = LanguageScore(speaking=6.0, writing=6.0, listening=6.0, reading=6.0)  # CLB7
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS, detail_scores=score, is_first_language=True
            ),
            french=None,
        ),
        education=Education(
            level=EducationLevel.BACHELOR, from_canada=True, has_COQ=False
        ),
        work_experience=Experience(canada_years=1, foreign_years=1),
    )
    result = crs_service._skill_transferability_points(profile)
    # education_language=13, education_can_exp=13, foreign_exp_lang=13,
    # foreign_can_exp=13, trade_lang=0 (has_COQ False)
    assert result == 13 + 13 + 13 + 13 + 0


def test_skill_transferability_points_capped_at_100(crs_service):
    """Construct a profile where the raw sum would exceed 100."""
    score = LanguageScore(speaking=7.0, writing=7.0, listening=8.0, reading=7.0)  # CLB9
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS, detail_scores=score, is_first_language=True
            ),
            french=None,
        ),
        education=Education(
            level=EducationLevel.BACHELOR, from_canada=True, has_COQ=True
        ),
        work_experience=Experience(canada_years=2, foreign_years=1),
    )
    result = crs_service._skill_transferability_points(profile)
    # Raw sum is 25 + 25 + 25 + 25 + 50 = 150, capped at 100.
    assert result == 100


# ---- _canadian_study_points ----
def test_canadian_study_points_no_canada_education_returns_zero(crs_service):
    assert crs_service._canadian_study_points(UserProfile(canada_education=None)) == 0


def test_canadian_study_points_not_completed_returns_zero(crs_service):
    profile = UserProfile(
        canada_education=CanadaEducation(completed=False, credential_years=0)
    )
    assert crs_service._canadian_study_points(profile) == 0


def test_canadian_study_points_zero_credential_years_returns_zero(crs_service):
    profile = UserProfile(
        canada_education=CanadaEducation(completed=True, credential_years=0)
    )
    assert crs_service._canadian_study_points(profile) == 0


def test_canadian_study_points_two_years_or_less_returns_15(crs_service):
    one_year = UserProfile(
        canada_education=CanadaEducation(completed=True, credential_years=1)
    )
    two_years = UserProfile(
        canada_education=CanadaEducation(completed=True, credential_years=2)
    )
    assert crs_service._canadian_study_points(one_year) == 15
    assert crs_service._canadian_study_points(two_years) == 15


def test_canadian_study_points_more_than_two_years_returns_30(crs_service):
    profile = UserProfile(
        canada_education=CanadaEducation(completed=True, credential_years=3)
    )
    assert crs_service._canadian_study_points(profile) == 30


# ---- _french_bonus_points ----
def test_french_bonus_points_no_french_returns_zero(crs_service):
    assert crs_service._french_bonus_points(UserProfile(languages=None)) == 0

    score = LanguageScore(speaking=7.5, writing=7.5, listening=8.5, reading=8.0)
    profile = UserProfile(
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS, detail_scores=score, is_first_language=True
            ),
            french=None,
        )
    )
    assert crs_service._french_bonus_points(profile) == 0


def test_french_bonus_points_nclc_below_7_returns_zero(crs_service):
    # TCF scores chosen to all land on NCLC 6 (below the 7 bonus floor).
    score = LanguageScore(speaking=7, writing=7, listening=400, reading=410)
    profile = UserProfile(
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TCF, detail_scores=score, is_first_language=True
            ),
            english=None,
        )
    )
    assert crs_service._french_bonus_points(profile) == 0


def test_french_bonus_points_nclc7_plus_no_or_low_english_returns_25(crs_service):
    """NCLC7+ and (no English result, or English CLB below 5) -> 25."""
    fr_score = LanguageScore(
        speaking=10, writing=10, listening=458, reading=453
    )  # NCLC7

    no_english = UserProfile(
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TCF, detail_scores=fr_score, is_first_language=True
            ),
            english=None,
        )
    )
    assert crs_service._french_bonus_points(no_english) == 25

    eng_score = LanguageScore(
        speaking=4.0, writing=4.0, listening=4.5, reading=3.5
    )  # CLB4
    low_english = UserProfile(
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TCF, detail_scores=fr_score, is_first_language=True
            ),
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=eng_score,
                is_first_language=False,
            ),
        )
    )
    assert crs_service._french_bonus_points(low_english) == 25


def test_french_bonus_points_nclc7_plus_clb5_plus_returns_50(crs_service):
    fr_score = LanguageScore(
        speaking=10, writing=10, listening=458, reading=453
    )  # NCLC7
    eng_score = LanguageScore(
        speaking=5.0, writing=5.0, listening=5.0, reading=5.0
    )  # CLB5+
    profile = UserProfile(
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TCF, detail_scores=fr_score, is_first_language=True
            ),
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=eng_score,
                is_first_language=False,
            ),
        )
    )
    assert crs_service._french_bonus_points(profile) == 50


# ---- calculate_crs ----
def test_calculate_crs_single_applicant_end_to_end(crs_service):
    """No spouse_breakdown attached; total matches sum of breakdown fields."""
    profile = UserProfile(
        age=30,
        marital_status=MaritalStatus.SINGLE,
        education=Education(level=EducationLevel.BACHELOR, from_canada=True),
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=LanguageScore(
                    speaking=7.5, writing=7.5, listening=8.5, reading=8.0
                ),
                is_first_language=True,
            ),
            french=None,
        ),
        work_experience=Experience(canada_years=2, foreign_years=1),
    )
    result = crs_service.calculate_crs(profile)
    assert result.spouse_breakdown is None
    assert result.total == sum(result.breakdown.model_dump().values())


def test_calculate_crs_married_applicant_includes_spouse_breakdown(crs_service):
    profile = UserProfile(
        age=30,
        marital_status=MaritalStatus.MARRIED,
        education=Education(level=EducationLevel.BACHELOR, from_canada=True),
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=LanguageScore(
                    speaking=7.5, writing=7.5, listening=8.5, reading=8.0
                ),
                is_first_language=True,
            ),
            french=None,
        ),
        work_experience=Experience(canada_years=2, foreign_years=1),
        spouse=SpouseProfile(
            education=Education(level=EducationLevel.BACHELOR, from_canada=True),
            canadian_experience=1,
        ),
    )
    result = crs_service.calculate_crs(profile)
    assert result.spouse_breakdown is not None
    assert result.breakdown.spouse_total == (
        result.spouse_breakdown.education
        + result.spouse_breakdown.language
        + result.spouse_breakdown.canadian_experience
    )
    assert result.total == sum(result.breakdown.model_dump().values())


def test_calculate_crs_additional_points_under_600_not_capped(crs_service):
    """provincial_nomination + french_bonus + sibling_in_canada +
    canadian_study <= 600 -> total is the plain sum."""
    fr_score = LanguageScore(
        speaking=10, writing=10, listening=458, reading=453
    )  # NCLC7
    eng_score = LanguageScore(
        speaking=5.0, writing=5.0, listening=5.0, reading=5.0
    )  # CLB5+
    profile = UserProfile(
        age=30,
        marital_status=MaritalStatus.SINGLE,
        sibling_in_can=True,
        education=Education(level=EducationLevel.BACHELOR, from_canada=True),
        canada_education=CanadaEducation(completed=True, credential_years=3),  # 30 pts
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TCF, detail_scores=fr_score, is_first_language=True
            ),
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=eng_score,
                is_first_language=False,
            ),
        ),
    )
    result = crs_service.calculate_crs(profile)
    additional = (
        result.breakdown.provincial_nomination
        + result.breakdown.french_bonus
        + result.breakdown.sibling_in_canada
        + result.breakdown.canadian_study
    )
    assert additional == 95  # 0 + 50 + 15 + 30
    assert additional <= 600
    assert result.total == sum(result.breakdown.model_dump().values())


def test_calculate_crs_additional_points_over_600_are_capped(crs_service):
    """Construct a profile where additional points exceed 600 (e.g.
    provincial_nomination=True contributes 600 alone, plus french_bonus,
    sibling_in_can, and canadian study credits) and assert the capped
    total formula in CRSService.calculate_crs is applied correctly.
    """
    fr_score = LanguageScore(
        speaking=10, writing=10, listening=458, reading=453
    )  # NCLC7
    eng_score = LanguageScore(
        speaking=5.0, writing=5.0, listening=5.0, reading=5.0
    )  # CLB5+
    profile = UserProfile(
        age=30,
        marital_status=MaritalStatus.SINGLE,
        provincial_nomination=True,
        sibling_in_can=True,
        education=Education(level=EducationLevel.BACHELOR, from_canada=True),
        canada_education=CanadaEducation(completed=True, credential_years=3),
        languages=Languages(
            french=FrenchScore(
                test_name=FrenchTest.TCF, detail_scores=fr_score, is_first_language=True
            ),
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                detail_scores=eng_score,
                is_first_language=False,
            ),
        ),
    )
    result = crs_service.calculate_crs(profile)
    additional = (
        result.breakdown.provincial_nomination
        + result.breakdown.french_bonus
        + result.breakdown.sibling_in_canada
        + result.breakdown.canadian_study
    )
    assert additional == 695  # 600 + 50 + 15 + 30
    raw_sum = sum(result.breakdown.model_dump().values())
    expected_total = raw_sum - additional + 600
    assert result.total == expected_total
    # Sanity check that capping actually reduced the total vs. the raw sum.
    assert result.total < raw_sum
