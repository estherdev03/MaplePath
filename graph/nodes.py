from graph.state.profile import ProfileDraft
from graph.state.shared import MainState, UserProfile
from user_profile.service import ProfileService


# Profile related nodes
def make_profile_parser(profile_service: ProfileService):
    def profile_parser(state: MainState) -> ProfileDraft:
        return profile_service.parse(profile_text=state.event.payload.text)

    return profile_parser


def make_create_profile(profile_service: ProfileService):
    def create_profile(state: MainState) -> MainState:
        return {"profile": profile_service.create(profile=state.event.payload)}

    return create_profile
