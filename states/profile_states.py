from datetime import UTC, datetime
from typing import Literal, Union

from pydantic import BaseModel, Field, model_validator


# Languages
class LanguageScore(BaseModel):
    speaking: float | None = None
    writing: float | None = None
    listening: float | None = None
    reading: float | None = None


class EnglishScore(BaseModel):
    test_name: Literal["ielts", "pte", "celpip"]
    overal_score: float | None = None
    detail_scores: LanguageScore | None = None


class FrenchScore(BaseModel):
    test_name: Literal["tef", "tcf"]
    overal_score: float | None = None
    detail_scores: LanguageScore | None


class Languages(BaseModel):
    english: EnglishScore | None
    french: FrenchScore | None

    @model_validator(mode="after")
    def validate_languages(self):
        if self.english == None and self.french == None:
            raise ValueError("Either English or French must be provided.")
        return self


# Working experience
class Experience(BaseModel):
    total_years: float = 0
    canada_years: float = 0
    alberta_years: float = 0


# CRS
class CRSBreakdown(BaseModel):
    age: int = 0
    education: int = 0
    first_language: int = 0
    second_language: int = 0
    canadian_experience: int = 0

    spouse: int = 0

    skill_transferability: int = 0

    provincial_nomation: int = 0
    arranged_employment: int = 0
    canadian_study: int = 0
    french_bonus: int = 0
    sibling_in_canada: int = 0


class CRSScore(BaseModel):
    total: int
    breakdown: CRSBreakdown


# Eligibility
class ProgramEligibility(BaseModel):
    eligible: bool
    reasons: list[str] = []
    gaps: list[str] = []


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


# User state
class UserProfile(BaseModel):
    age: int | None = None

    job_title: str | None = None
    noc_code: str | None = None

    languages: Languages | None = None

    work_experience: Experience | None = None

    crs_score: CRSScore | None = None

    eligibility: Eligibility | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    profile_version: int | None = None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        setattr(self, "updated_at", datetime.now(UTC))


# Profile payload
class ProfileConfirmFormPayload(BaseModel):
    age: int
    languages: Languages
    job_title: str
    work_experience: Experience


class ProfileDraftPayload(BaseModel):
    text: str


class ProfileUpdateFormPayload(ProfileConfirmFormPayload):
    fields_updated: list[str] | None = None


class ProfileDraft(BaseModel):
    age: int | None = None
    languages: Languages | None = None
    job_title: str | None = None
    work_experience: Experience | None = None

    missing_fields: list[str] | None = None
    warnings: list[str] | None = None


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
