"""Tests for graph.state.shared.UserProfile and MainState."""

from graph.state.profile import ProfileDraft, ProfileDraftEvent, ProfileDraftPayload
from graph.state.shared import MainState, UserProfile


def test_user_profile_defaults():
    """provincial_nomination/sibling_in_can/relative_in_can default False;
    current_available_funds defaults 0; optional fields default None."""
    profile = UserProfile()
    assert profile.provincial_nomination is False
    assert profile.sibling_in_can is False
    assert profile.relative_in_can is False
    assert profile.current_available_funds == 0
    assert profile.age is None
    assert profile.crs_score is None


def test_user_profile_update_sets_fields_and_bumps_updated_at():
    profile = UserProfile()
    original_updated_at = profile.updated_at
    profile.update(age=30)
    assert profile.age == 30
    assert profile.updated_at >= original_updated_at


def test_main_state_accepts_profile_draft_or_user_profile():
    """profile: UserProfile | ProfileDraft -- both should validate."""
    event = ProfileDraftEvent(
        event_type="profile_draft", payload=ProfileDraftPayload(text="hi")
    )
    state_with_draft = MainState(event=event, profile=ProfileDraft())
    state_with_user = MainState(event=event, profile=UserProfile())
    assert isinstance(state_with_draft.profile, ProfileDraft)
    assert isinstance(state_with_user.profile, UserProfile)
