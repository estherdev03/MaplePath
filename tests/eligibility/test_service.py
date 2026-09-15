"""Tests for eligibility.service.EligibilityService."""

from graph.state.profile import (
    CanadaEducation,
    CLBScore,
    Education,
    EducationLevel,
    EnglishScore,
    EnglishTest,
    Experience,
    FrenchScore,
    FrenchTest,
    Languages,
    NCLCScore,
    Occupation,
    SpouseProfile,
)
from graph.state.shared import UserProfile


def _occ(**kw):
    return Occupation(title="x", **kw)


# ---- _calculate_fsw ----
def test_calculate_fsw_education_language_and_work_points(eligibility_service):
    """Education table, CLB7+-only first-language points, and the combined
    work-experience-years cap all feed the FSW selection score."""
    user = UserProfile(
        education=Education(level=EducationLevel.PHD, from_canada=True),  # 25
        languages=Languages(
            english=EnglishScore(
                test_name=EnglishTest.IELTS,
                is_first_language=True,
                clb_scores=CLBScore(speaking=10, writing=6, listening=8, reading=7),
            ),
            french=None,
        ),
        work_experience=Experience(canada_years=5, foreign_years=5),  # capped at 6yrs
        occupation=_occ(have_canada_job_offer=False),
    )
    _, breakdown = eligibility_service._calculate_fsw(user)
    assert breakdown.education_pts == 25
    # writing=6 is below the CLB7 floor and earns nothing.
    assert breakdown.first_lang_pts == 6 + 5 + 4  # FIRST_LANGUAGE_POINTS[10, 8, 7]
    assert breakdown.work_exp_pts == 15  # WORK_EXPERIENCE_POINTS[6] (capped)


def test_calculate_fsw_work_exp_with_fractional_years_does_not_raise(
    eligibility_service,
):
    """canada_years/foreign_years are floats; combined total must be cast to
    int before indexing WORK_EXPERIENCE_POINTS or a fractional sum (e.g. 2.5)
    raises a KeyError instead of scoring correctly."""
    user = UserProfile(
        work_experience=Experience(canada_years=1.5, foreign_years=1.0),
        occupation=_occ(have_canada_job_offer=False),
    )
    _, breakdown = eligibility_service._calculate_fsw(user)
    assert breakdown.work_exp_pts == 11  # WORK_EXPERIENCE_POINTS[int(2.5) == 2]


def test_calculate_fsw_age_points_capped_and_below_18(eligibility_service):
    below = UserProfile(age=17, occupation=_occ(have_canada_job_offer=False))
    capped = UserProfile(age=60, occupation=_occ(have_canada_job_offer=False))
    _, b_below = eligibility_service._calculate_fsw(below)
    _, b_capped = eligibility_service._calculate_fsw(capped)
    assert b_below.age_pts == 0
    assert b_capped.age_pts == 1  # AGE_POINTS[46] via the min(age, 46) cap


def test_calculate_fsw_employment_and_adaptability_capped(eligibility_service):
    """A job offer grants employment points plus an adaptability factor;
    stacking enough adaptability factors is capped at ADAPTABILITY_MAX."""
    user = UserProfile(
        occupation=_occ(teer=1, have_canada_job_offer=True),
        work_experience=Experience(canada_years=2),
        canada_education=CanadaEducation(completed=True, credential_years=2),
        relative_in_can=True,
    )
    _, breakdown = eligibility_service._calculate_fsw(user)
    assert breakdown.employment_pts == 10
    assert breakdown.adaptability_pts == 10  # capped even though factors sum higher


# ---- _evaluate_federal_skilled_worker ----
def test_fsw_teer_language_and_education_gates(eligibility_service):
    eng = EnglishScore(
        test_name=EnglishTest.IELTS,
        is_first_language=True,
        clb_scores=CLBScore(speaking=7, writing=7, listening=7, reading=7),
    )
    fr = FrenchScore(
        test_name=FrenchTest.TCF,
        is_first_language=False,
        detail_scores=None,
        nclc_scores=NCLCScore(speaking=5, writing=5, listening=5, reading=5),
    )
    good = UserProfile(
        occupation=_occ(teer=1, have_canada_job_offer=False),
        languages=Languages(english=eng, french=fr),
        education=Education(level=EducationLevel.BACHELOR, from_canada=True),
    )
    result = eligibility_service._evaluate_federal_skilled_worker(good)
    assert result.eligible_teer_met is True
    assert result.language_requirement_met is True
    assert result.education_requirement_met is True

    # TEER outside [0-3], CLB dropped below 7, and missing education all
    # flip their respective gates.
    eng_weak = EnglishScore(
        test_name=EnglishTest.IELTS,
        is_first_language=True,
        clb_scores=CLBScore(speaking=6, writing=7, listening=7, reading=7),
    )
    bad = UserProfile(
        occupation=_occ(teer=5, have_canada_job_offer=False),
        languages=Languages(english=eng_weak, french=fr),
        education=None,
    )
    result_bad = eligibility_service._evaluate_federal_skilled_worker(bad)
    assert result_bad.eligible_teer_met is False
    assert result_bad.language_requirement_met is False
    assert result_bad.education_requirement_met is False


def test_fsw_settlement_funds_thresholds_and_job_offer_bypass(eligibility_service):
    """Settlement funds threshold single: 15263; with spouse: 19001. Client bypasses
    when there is a job offer."""
    no_spouse = UserProfile(
        current_available_funds=15263, occupation=_occ(have_canada_job_offer=False)
    )
    with_spouse = UserProfile(
        current_available_funds=19001,
        spouse=SpouseProfile(),
        occupation=_occ(have_canada_job_offer=False),
    )
    job_offer = UserProfile(
        current_available_funds=0, occupation=_occ(have_canada_job_offer=True)
    )

    assert (
        eligibility_service._evaluate_federal_skilled_worker(
            no_spouse
        ).settlement_funds_met
        is True
    )
    assert (
        eligibility_service._evaluate_federal_skilled_worker(
            with_spouse
        ).settlement_funds_met
        is True
    )
    result = eligibility_service._evaluate_federal_skilled_worker(job_offer)
    assert result.settlement_funds_required is False


def test_fsw_selection_factor_passed_at_exactly_67(eligibility_service):
    """Score == FSW_PASS_SCORE (67) -> passed; 66 -> not passed."""

    def build(age):
        return UserProfile(
            age=age,
            education=Education(level=EducationLevel.PHD, from_canada=True),  # 25
            languages=Languages(
                english=EnglishScore(
                    test_name=EnglishTest.IELTS,
                    is_first_language=True,
                    clb_scores=CLBScore(
                        speaking=10, writing=10, listening=10, reading=10
                    ),
                ),
                french=None,
            ),  # +24
            work_experience=Experience(canada_years=3, foreign_years=3),  # +15 (6yrs)
            occupation=_occ(have_canada_job_offer=False),
        )

    passed = eligibility_service._evaluate_federal_skilled_worker(build(44))  # +3 age
    not_passed = eligibility_service._evaluate_federal_skilled_worker(
        build(45)
    )  # +2 age
    assert passed.selection_factor_score == 67
    assert passed.selection_factor_passed is True
    assert not_passed.selection_factor_score == 66
    assert not_passed.selection_factor_passed is False


# ---- _evaluate_canadian_exp_class ----
def test_cec_gates_and_teer_dependent_language_requirement(eligibility_service):
    """TEER 0/1 needs CLB7+; TEER 2/3 needs CLB5+; TEER 4/5 never satisfies
    the language gate (documented quirk, not a fix -- see source)."""
    work = Experience(canada_work_exp_within_3_years=1, canada_years=1)
    eng7 = EnglishScore(
        test_name=EnglishTest.IELTS,
        is_first_language=True,
        clb_scores=CLBScore(speaking=7, writing=7, listening=7, reading=7),
    )
    eng5 = EnglishScore(
        test_name=EnglishTest.IELTS,
        is_first_language=True,
        clb_scores=CLBScore(speaking=5, writing=5, listening=5, reading=5),
    )

    teer1 = UserProfile(
        work_experience=work,
        occupation=_occ(teer=1),
        languages=Languages(english=eng7, french=None),
    )
    result1 = eligibility_service._evaluate_canadian_exp_class(teer1)
    assert result1.canadian_work_experience_met is True
    assert result1.eligible_teer_met is True
    assert result1.language_requirement_met is True

    teer2_clb5 = UserProfile(
        work_experience=work,
        occupation=_occ(teer=2),
        languages=Languages(english=eng5, french=None),
    )
    assert (
        eligibility_service._evaluate_canadian_exp_class(
            teer2_clb5
        ).language_requirement_met
        is True
    )

    # CLB5 isn't enough for TEER 0/1, which needs CLB7+.
    teer1_clb5 = UserProfile(
        work_experience=work,
        occupation=_occ(teer=1),
        languages=Languages(english=eng5, french=None),
    )
    assert (
        eligibility_service._evaluate_canadian_exp_class(
            teer1_clb5
        ).language_requirement_met
        is False
    )

    teer4 = UserProfile(
        work_experience=work,
        occupation=_occ(teer=4),
        languages=Languages(english=eng7, french=None),
    )
    assert (
        eligibility_service._evaluate_canadian_exp_class(teer4).language_requirement_met
        is False
    )


# ---- _evaluate_federal_skilled_trades ----
def test_fst_eligible_trade_matches_and_excludes(eligibility_service):
    """major/minor/noc_code match makes a trade eligible, except the two
    explicit major+submajor exclusions."""
    matched = UserProfile(
        occupation=_occ(major_group_code="72", submajor_group_code="721")
    )
    excluded = UserProfile(
        occupation=_occ(major_group_code="72", submajor_group_code="726")
    )
    unmatched = UserProfile(occupation=_occ(major_group_code="11"))

    assert (
        eligibility_service._evaluate_federal_skilled_trades(matched).eligible_trade_met
        is True
    )
    assert (
        eligibility_service._evaluate_federal_skilled_trades(
            excluded
        ).eligible_trade_met
        is False
    )
    assert (
        eligibility_service._evaluate_federal_skilled_trades(
            unmatched
        ).eligible_trade_met
        is False
    )


def test_fst_language_and_job_offer_or_certificate(eligibility_service):
    eng = EnglishScore(
        test_name=EnglishTest.IELTS,
        is_first_language=True,
        clb_scores=CLBScore(speaking=5, listening=5, reading=4, writing=4),
    )
    coq_user = UserProfile(
        languages=Languages(english=eng, french=None),
        education=Education(level=EducationLevel.BACHELOR, has_COQ=True),
    )
    result = eligibility_service._evaluate_federal_skilled_trades(coq_user)
    assert result.speaking_listening_requirement_met is True
    assert result.reading_writing_requirement_met is True
    assert (
        result.valid_job_offer_or_certificate_met is True
    )  # via has_COQ, no job offer needed

    job_offer_user = UserProfile(occupation=_occ(have_canada_job_offer=True))
    result2 = eligibility_service._evaluate_federal_skilled_trades(job_offer_user)
    assert result2.valid_job_offer_or_certificate_met is True
    assert result2.settlement_funds_required is False


# ---- evaluate_express_entry ----
def test_evaluate_express_entry_returns_all_three_program_results(eligibility_service):
    user = UserProfile(occupation=_occ(have_canada_job_offer=False))
    result = eligibility_service.evaluate_express_entry(user)
    assert result.federal_skilled_worker is not None
    assert result.federal_skilled_trade is not None
    assert result.canadian_exp_class is not None
    # A bare profile with nothing filled in should qualify for none of them.
    assert result.federal_skilled_worker.eligible is False
    assert result.federal_skilled_trade.eligible is False
    assert result.canadian_exp_class.eligible is False
