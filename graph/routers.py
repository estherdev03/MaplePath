from typing import Literal
from langgraph.types import Command

from graph.state.shared import MainState


def orchestrator(
    state: MainState,
) -> Command[Literal["profile_router"]]:
    if state.event.event_type.startswith("profile_"):
        return Command(goto="profile_router")


def profile_router(
    state: MainState,
) -> Command[Literal["parse_profile", "create_profile"]]:
    print(state.event.event_type)
    if state.event.event_type == "profile_draft":
        return Command(goto="parse_profile")
    elif state.event.event_type == "profile_confirm":
        return Command(goto="create_profile")
