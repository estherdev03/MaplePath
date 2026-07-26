from enum import StrEnum
from typing import Union

from pydantic import BaseModel


# Express Entry
class EEProgram(StrEnum):
    FSW = "Federal Skilled Worker"
    CEC = "Canadian Experience Class"
    FST = "Federal Skilled Trades"


class FSWScoreBreakdown(BaseModel):
    education_pts: int = 0
    first_lang_pts: int = 0
    second_lang_pts: int = 0
    work_exp_pts: int = 0
    age_pts: int = 0
    employment_pts: int = 0
    adaptability: int = 0


class FederalSkilledWorkerEligibility(BaseModel):
    # Work experience
    continuous_work_experience: bool = False
    eligible_teer: bool = False

    # Language
    language_requirement_met: bool = False

    # Education
    education_requirement_met: bool = False

    # Selection factors
    selection_factor_breakdown: FSWScoreBreakdown | None = None
    selection_factor_score: int = 0
    selection_factor_passed: bool = False

    # Settlement funds
    settlement_funds_required: bool = True
    settlement_funds_met: bool = False


class CanadianExperienceClassEligibility(BaseModel):
    # Canadian work experience
    canadian_work_experience: bool = False
    work_experience_within_3_years: bool = False
    eligible_teer: bool = False

    # Language
    required_clb: int = 7
    language_requirement_met: bool = False

    # Education (optional)
    education_present: bool = False

    # Settlement funds
    settlement_funds_required: bool = False


class FederalSkilledTradesEligibility(BaseModel):
    # Skilled trade experience
    skilled_trade_experience: bool = False
    work_experience_within_5_years: bool = False
    eligible_trade: bool = False

    # Language
    speaking_listening_requirement_met: bool = False
    reading_writing_requirement_met: bool = False

    # Qualification
    valid_job_offer: bool = False
    certificate_of_qualification: bool = False

    # Job requirements
    trade_requirements_met: bool = False


class ExpressEntryEligibility(BaseModel):
    has_profile: bool
    profile_number: str | None
    program: EEProgram
    breakdown: Union[
        FederalSkilledWorkerEligibility,
        CanadianExperienceClassEligibility,
        FederalSkilledTradesEligibility,
    ]


# Overall Eligibility
class EligibilityResult(BaseModel):
    eligible: bool
    score: float
    reasons: list[str]
    missing_requirements: list[str]
    breakdown: ExpressEntryEligibility


class EligibilityReport(BaseModel):
    express_entry: EligibilityResult
    alberta_opportunity: EligibilityResult
    accelerated_tech: EligibilityResult
    rural_renewal: EligibilityResult
    tourism_hospitality: EligibilityResult
