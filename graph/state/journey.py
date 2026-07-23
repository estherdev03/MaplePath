from typing import Literal

from pydantic import BaseModel


class JourneyUpdatePayload(BaseModel):
    pass


class JourneyEvent(BaseModel):
    event_type: Literal["journey_update"]
    payload: JourneyUpdatePayload
