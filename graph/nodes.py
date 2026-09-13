from graph.state.profile import ProfileDraft
from graph.state.shared import MainState, UserProfile
from user_profile.service import ProfileService


# Profile related nodes
def parse_profile_wrapper(profile_service: ProfileService):
    def parse_profile(state: MainState) -> ProfileDraft:
        return {"profile": profile_service.parse(profile_text=state.event.payload.text)}

    return parse_profile


def create_profile_wrapper(profile_service: ProfileService):
    def create_profile(state: MainState) -> dict:
        return {"profile": profile_service.create(profile=state.event.payload)}

    return create_profile


def calculate_crs_wrapper(profile_service: ProfileService):
    def calculate_crs(state: MainState) -> dict:
        return {"profile": profile_service.calculate_CRS(state.profile)}

    return calculate_crs


def evaluate_eligibility_wrapper(profile_service: ProfileService):
    def evaluate_eligibility(state: MainState) -> dict:
        return {"profile": profile_service.evaluate_express_entry(state.profile)}

    return evaluate_eligibility
