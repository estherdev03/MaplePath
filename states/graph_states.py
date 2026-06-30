from typing import Union

from pydantic import BaseModel

from states.chat_states import ChatEvent
from states.journey_states import JourneyUpdateEvent
from states.profile_states import ProfileEvent, UserProfile

InputEvent = Union[ProfileEvent, ChatEvent, JourneyUpdateEvent]


class UserState(BaseModel):
    event: InputEvent
    profile: UserProfile | None = None


class OutputState(BaseModel):
    profile: UserProfile | None = None
