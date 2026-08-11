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
    adaptability_pts: int = 0


class FederalSkilledWorkerEligibility(BaseModel):
    # Work experience
    continuous_work_experience_met: bool = False
    eligible_teer_met: bool = False

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
    canadian_work_experience_met: bool = False
    eligible_teer_met: bool = False

    # Language
    language_requirement_met: bool = False


class FederalSkilledTradesEligibility(BaseModel):
    # Skilled trade experience
    skilled_trade_experience_within_5_years_met: bool = False
    eligible_trade_met: bool = False

    # Language
    speaking_listening_requirement_met: bool = False
    reading_writing_requirement_met: bool = False

    # Qualification
    valid_job_offer_or_certificate_met: bool = False

    # Settlement funds
    settlement_funds_required: bool = True
    settlement_funds_met: bool = False


class EligibilityResult(BaseModel):
    eligible: bool = False
    breakdown: Union[
        FederalSkilledWorkerEligibility,
        FederalSkilledTradesEligibility,
        CanadianExperienceClassEligibility,
        None,
    ] = None


class ExpressEntryEligibility(BaseModel):
    federal_skilled_worker: EligibilityResult | None = None
    federal_skilled_trade: EligibilityResult | None = None
    canadian_exp_class: EligibilityResult | None = None
