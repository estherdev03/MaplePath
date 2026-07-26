from typing import Union
from datetime import datetime, UTC

from pydantic import BaseModel, Field

from graph.state.chat import ChatEvent
from graph.state.journey import JourneyEvent
from graph.state.profile import (
    ProfileEvent,
    Occupation,
    Languages,
    Experience,
    MaritalStatus,
    Education,
    CanadaEducation,
    SpouseProfile,
    CRSScore,
    Eligibility,
)
from user_profile.service import ProfileService

InputEvent = Union[ProfileEvent, ChatEvent, JourneyEvent]


# Main user state
class UserProfile(BaseModel):
    age: int | None = None

    occupation: Occupation | None = None

    languages: Languages | None = None

    work_experience: Experience | None = None

    marital_status: MaritalStatus | None = None

    education: Education | None = None

    canada_education: CanadaEducation | None = None

    provincial_nomination: bool = False

    sibling_in_can: bool = False

    relative_in_can: bool = False

    spouse: SpouseProfile | None = None

    crs_score: CRSScore | None = None

    eligibility: Eligibility | None = None

    current_available_funds: float = 0

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    profile_version: int | None = None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        setattr(self, "updated_at", datetime.now(UTC))


# Input state
class MainState(BaseModel):
    event: InputEvent
    profile: UserProfile | None = None


# Output state
class OutputState(BaseModel):
    profile: UserProfile | None = None
