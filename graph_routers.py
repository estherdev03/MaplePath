from typing import Literal

from langgraph.types import Command

from states.graph_states import UserState


def orchestrator(
    state: UserState,
) -> Command[Literal["profile_router"]]:
    if state.event.event_type.startswith("profile_"):
        return Command(goto="profile_router")


def profile_router(state: UserState) -> Command[Literal["profile_parser"]]:
    print(state.event.event_type)
    if state.event.event_type == "profile_draft":
        return Command(goto="profile_parser")
