from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# Languages
class LanguageScore(BaseModel):
    speaking: float
    writing: float
    listening: float
    reading: float


class EnglishScore(BaseModel):
    test_name: Literal["ielts", "pte", "celpip"]
    score: LanguageScore


class FrenchScore(BaseModel):
    test_name: Literal["tef", "tcf"]
    score: LanguageScore


class Languages(BaseModel):
    english: EnglishScore
    french: FrenchScore


# Working experience
class Experience(BaseModel):
    total_years: float = 0
    canada_years: float = 0
    alberta_years: float = 0


# Profile form
class ProfileFormPayload(BaseModel):
    age: int | None = None
    languages: Languages | None = None
    job_title: str | None = None
    work_experience: Experience | None = None


# Profile payload
class ProfileUpdatePayload(BaseModel):
    source: Literal["chat", "form"]
    profile_version: int | None = 1
    text: str | None = None
    profile: ProfileFormPayload | None = None

    @model_validator(mode="after")
    def validate_input(self):
        if self.text is None or self.profile is None:
            raise ValueError("Either text or profile must be provided.")
        return self


# Profile update event
class ProfileUpdateEvent(BaseModel):
    event_type: Literal["profile_update"]
    payload: ProfileUpdatePayload


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

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        setattr(self, "updated_at", datetime.now(UTC))
