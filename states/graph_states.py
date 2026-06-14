from typing import Union

from states.chat_states import ChatEvent
from states.journey_states import JourneyUpdateEvent
from states.profile_states import ProfileUpdateEvent

InputState = Union[ProfileUpdateEvent, ChatEvent, JourneyUpdateEvent]
