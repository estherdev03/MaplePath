"""Tests for graph.state.eligibility Pydantic models."""

from graph.state.eligibility import (
    EligibilityResult,
    ExpressEntryEligibility,
    FSWScoreBreakdown,
)


def test_fsw_score_breakdown_defaults_to_zero_for_all_point_fields():
    """EligibilityService._calculate_fsw relies on
    sum(fsw_score.model_dump().values()) starting from well-defined
    defaults."""
    assert all(v == 0 for v in FSWScoreBreakdown().model_dump().values())


def test_eligibility_result_defaults_not_eligible_with_no_breakdown():
    result = EligibilityResult()
    assert result.eligible is False
    assert result.breakdown is None


def test_express_entry_eligibility_holds_all_three_program_results():
    ee = ExpressEntryEligibility(
        federal_skilled_worker=EligibilityResult(eligible=True),
        federal_skilled_trade=EligibilityResult(eligible=False),
        canadian_exp_class=EligibilityResult(eligible=False),
    )
    assert ee.federal_skilled_worker.eligible is True
    assert ee.federal_skilled_trade.eligible is False
    assert ee.canadian_exp_class.eligible is False
