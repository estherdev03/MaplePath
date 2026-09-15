import logging

from graph.state.profile import ProfileDraft
from graph.state.shared import MainState, UserProfile
from user_profile.service import ProfileService

logger = logging.getLogger(__name__)


# Profile related nodes
def parse_profile_wrapper(profile_service: ProfileService):
    def parse_profile(state: MainState) -> ProfileDraft:
        logger.debug("Entering node: parse_profile")
        return {"profile": profile_service.parse(profile_text=state.event.payload.text)}

    return parse_profile


def create_profile_wrapper(profile_service: ProfileService):
    def create_profile(state: MainState) -> dict:
        logger.debug("Entering node: create_profile")
        return {"profile": profile_service.create(profile=state.event.payload)}

    return create_profile


def calculate_crs_wrapper(profile_service: ProfileService):
    def calculate_crs(state: MainState) -> dict:
        logger.debug("Entering node: calculate_crs")
        return {"profile": profile_service.calculate_CRS(state.profile)}

    return calculate_crs


def evaluate_eligibility_wrapper(profile_service: ProfileService):
    def evaluate_eligibility(state: MainState) -> dict:
        logger.debug("Entering node: evaluate_express_entry")
        return {"profile": profile_service.evaluate_express_entry(state.profile)}

    return evaluate_eligibility


def create_advice_wrapper(profile_service: ProfileService):
    def create_advice(state: MainState) -> dict:
        logger.debug("Entering node: create_advice")
        return {"profile": profile_service.create_advice(state.profile)}

    return create_advice
