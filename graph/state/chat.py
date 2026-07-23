from __future__ import annotations
from typing import Literal

from pydantic import BaseModel


class ChatPayload(BaseModel):
    pass


class ChatEvent(BaseModel):
    event_type: Literal["chat_message"]
    payload: ChatPayload
