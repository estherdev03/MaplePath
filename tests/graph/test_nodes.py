"""Tests for graph.nodes.*_wrapper factories."""

from unittest.mock import MagicMock

from graph.nodes import (
    calculate_crs_wrapper,
    create_advice_wrapper,
    create_profile_wrapper,
    evaluate_eligibility_wrapper,
    parse_profile_wrapper,
)
from graph.state.profile import ProfileDraftEvent, ProfileDraftPayload


def test_parse_profile_wrapper_calls_service_parse_with_event_text():
    """Reads state.event.payload.text, returns {"profile": ...}."""
    service = MagicMock()
    service.parse.return_value = "draft"
    node = parse_profile_wrapper(service)
    state = MagicMock(
        event=ProfileDraftEvent(
            event_type="profile_draft", payload=ProfileDraftPayload(text="hello")
        )
    )
    result = node(state)
    service.parse.assert_called_once_with(profile_text="hello")
    assert result == {"profile": "draft"}


def test_create_profile_wrapper_calls_service_create_with_event_payload():
    """Reads state.event.payload, returns {"profile": ...}."""
    service = MagicMock()
    service.create.return_value = "user"
    node = create_profile_wrapper(service)
    payload = MagicMock()
    state = MagicMock(event=MagicMock(payload=payload))
    result = node(state)
    service.create.assert_called_once_with(profile=payload)
    assert result == {"profile": "user"}


def test_calculate_crs_wrapper_calls_service_calculate_crs_with_state_profile():
    service = MagicMock()
    service.calculate_CRS.return_value = "scored"
    node = calculate_crs_wrapper(service)
    state = MagicMock(profile="profile")
    result = node(state)
    service.calculate_CRS.assert_called_once_with("profile")
    assert result == {"profile": "scored"}


def test_evaluate_eligibility_wrapper_calls_service_evaluate_express_entry():
    service = MagicMock()
    service.evaluate_express_entry.return_value = "eligibility"
    node = evaluate_eligibility_wrapper(service)
    state = MagicMock(profile="profile")
    result = node(state)
    service.evaluate_express_entry.assert_called_once_with("profile")
    assert result == {"profile": "eligibility"}


def test_create_advice_wrapper_calls_service_create_advice():
    service = MagicMock()
    service.create_advice.return_value = "advised"
    node = create_advice_wrapper(service)
    state = MagicMock(profile="profile")
    result = node(state)
    service.create_advice.assert_called_once_with("profile")
    assert result == {"profile": "advised"}
