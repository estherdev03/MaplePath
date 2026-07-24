from enum import StrEnum
from typing import Union

from pydantic import BaseModel


# Express Entry
class EEProgram(StrEnum):
    FSW = "Federal Skilled Worker"
    CEC = "Canadian Experience Class"
    FST = "Federal Skilled Trades"


class FederalSkilledWorkerEligibility(BaseModel):
    # Work experience
    skilled_work_experience: bool = False
    continuous_work_experience: bool = False
    work_experience_within_10_years: bool = False
    eligible_teer: bool = False

    # Language
    language_requirement_met: bool = False
    minimum_clb: int = 7

    # Education
    education_requirement_met: bool = False
    eca_required: bool = False
    eca_completed: bool = False

    # Selection factors
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
