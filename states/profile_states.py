from datetime import UTC, datetime
from enum import StrEnum
from fileinput import isfirstline
from typing import Literal, Union

from pydantic import BaseModel, Field, model_validator


class EducationLevel(StrEnum):
    SECONDARY = "secondary"
    ONE_YEAR = "one_year"
    TWO_YEAR = "two_year"
    BACHELOR = "bachelor"
    TWO_OR_MORE = "two_or_more_credentials"
    MASTERS = "masters"
    PHD = "phd"


class EnglishTest(StrEnum):
    IELTS = "ielts"
    CELPIP = "celpip"
    PTE = "pte"
    TEF = "tef"
    TCF = "tcf"


class FrenchTest(StrEnum):
    TEF = "tef"
    TCF = "tcf"


class MaritalStatus(StrEnum):
    SINGLE = "single"
    MARRIED = "married"


# Languages
class LanguageScore(BaseModel):
    speaking: float | None = None
    writing: float | None = None
    listening: float | None = None
    reading: float | None = None


class CLBScore(BaseModel):
    speaking: int
    writing: int
    listening: int
    reading: int


class NCLCScore(BaseModel):
    speaking: int
    writing: int
    listening: int
    reading: int


class EnglishScore(BaseModel):
    test_name: EnglishTest
    overall_score: float | None = None
    detail_scores: LanguageScore | None = None
    clb_scores: CLBScore | None = None
    is_first_language: bool = False


class FrenchScore(BaseModel):
    test_name: FrenchTest
    overall_score: float | None = None
    detail_scores: LanguageScore | None
    nclc_scores: NCLCScore | None = None
    is_first_language: bool = False


class Languages(BaseModel):
    english: EnglishScore | None
    french: FrenchScore | None

    @model_validator(mode="after")
    def validate_languages(self):
        if self.english == None and self.french == None:
            raise ValueError("Either English or French must be provided.")
        if self.english and self.french:
            if self.english.is_first_language and self.french.is_first_language:
                raise ValueError(
                    "First language conflict. Only one language can be chosen (Tips: choose the one with higher test score to maximize your CRS)"
                )
            if not self.english.is_first_language and not self.french.is_first_language:
                raise ValueError(
                    "Either English or French must be chosen as first language (Tips: choose the one with higher test score to maximize your CRS)"
                )
        if self.english and not self.french:
            self.english.is_first_language = True
        elif self.french and not self.english:
            self.french.is_first_language = True
        return self


# Working experience
class Experience(BaseModel):
    foreign_years: float = Field(default=0, ge=0)
    canada_years: float = Field(default=0, ge=0)
    alberta_years: float = Field(default=0, ge=0)


class SpouseBreakdown(BaseModel):
    education: int = 0
    language: int = 0
    canadian_experience: int = 0


# CRS
class CRSBreakdown(BaseModel):
    age: int = 0
    education: int = 0
    first_language: int = 0
    second_language: int = 0
    canadian_experience: int = 0

    spouse_total: int = 0

    skill_transferability: int = 0

    provincial_nomination: int = 0
    canadian_study: int = 0
    french_bonus: int = 0
    sibling_in_canada: int = 0


class CRSScore(BaseModel):
    total: int
    breakdown: CRSBreakdown
    spouse_breakdown: SpouseBreakdown | None = None


# Eligibility
class ProgramEligibility(BaseModel):
    eligible: bool
    reasons: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class ExpressEntryEligibility(ProgramEligibility):
    pass


class AlbertaTechEligibility(ProgramEligibility):
    pass


class AlbertaOpportunityEligibility(ProgramEligibility):
    pass


class Eligibility(BaseModel):
    express_entry: ExpressEntryEligibility
    alberta_opportunity: AlbertaOpportunityEligibility
    alberta_tech: AlbertaTechEligibility


# Education
class Education(BaseModel):
    level: EducationLevel
    has_COQ: bool = False
    from_canada: bool = True
    eca_completed: bool = False


class CanadaEducation(BaseModel):
    completed: bool
    credential_years: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_credential_years(self):
        if self.completed == False and self.credential_years > 0:
            raise ValueError("Credential years is invalid if not completed.")


# Spouse
class SpouseProfile(BaseModel):
    education: Education | None = None
    languages: Languages | None = None
    canadian_experience: float = 0


# Profile payload
class ProfileConfirmFormPayload(BaseModel):
    age: int
    languages: Languages
    job_title: str
    work_experience: Experience
    marital_status: MaritalStatus
    education: Education
    canada_education: CanadaEducation
    arranged_employment: bool = False
    provincial_nomination: bool = False
    sibling_in_can: bool = False

    spouse: SpouseProfile | None = None

    @model_validator(mode="after")
    def validate_spouse(self):
        if self.marital_status == MaritalStatus.MARRIED and self.spouse is None:
            raise ValueError("Spouse information is required for married applicants.")
        return self


class ProfileDraftPayload(BaseModel):
    text: str


class ProfileUpdateFormPayload(ProfileConfirmFormPayload):
    fields_updated: list[str] = Field(default_factory=list)


class ProfileDraft(BaseModel):
    age: int | None = None
    languages: Languages | None = None
    job_title: str | None = None
    work_experience: Experience | None = None
    education: Education | None = None
    canada_education: CanadaEducation | None = None
    arranged_employment: bool = False
    provincial_nomination: bool = False
    sibling_in_can: bool = False
    marital_status: MaritalStatus | None = None
    spouse: SpouseProfile | None = None

    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence_score: float = 0.0


# Profile events
class ProfileDraftEvent(BaseModel):
    event_type: Literal["profile_draft"]
    payload: ProfileDraftPayload


class ProfileConfirmEvent(BaseModel):
    event_type: Literal["profile_confirm"]
    payload: ProfileConfirmFormPayload


class ProfileUpdateEvent(BaseModel):
    event_type: Literal["profile_update"]
    payload: ProfileUpdateFormPayload


# Compound event
ProfileEvent = Union[ProfileDraftEvent, ProfileConfirmEvent, ProfileUpdateEvent]


# User state
class UserProfile(BaseModel):
    age: int | None = None

    job_title: str | None = None
    noc_code: str | None = None
    teer: int | None = None
    noc_confidence: float | None = None

    languages: Languages | None = None

    work_experience: Experience | None = None

    marital_status: MaritalStatus | None = None

    education: Education | None = None

    canada_education: CanadaEducation | None = None

    arranged_employment: bool = False

    provincial_nomination: bool = False

    sibling_in_can: bool = False

    spouse: SpouseProfile | None = None

    crs_score: CRSScore | None = None

    eligibility: Eligibility | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    profile_version: int | None = None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        setattr(self, "updated_at", datetime.now(UTC))
