"""Tests for graph.routers.orchestrator and profile_router."""

from unittest.mock import MagicMock

from graph.routers import orchestrator, profile_router


def _state(event_type):
    return MagicMock(event=MagicMock(event_type=event_type))


def test_orchestrator_routes_profile_prefixed_event_to_profile_router():
    command = orchestrator(_state("profile_draft"))
    assert command.goto == "profile_router"


def test_orchestrator_unmatched_event_type_returns_none():
    """event_type not starting with 'profile_' -> function falls through
    and returns None (no Command). Confirm this is the intended fallback."""
    assert orchestrator(_state("evaluate_noc")) is None


def test_profile_router_routes_profile_draft_to_parse_profile():
    command = profile_router(_state("profile_draft"))
    assert command.goto == "parse_profile"


def test_profile_router_routes_profile_confirm_to_create_profile():
    command = profile_router(_state("profile_confirm"))
    assert command.goto == "create_profile"


def test_profile_router_unrecognized_event_type_returns_none():
    assert profile_router(_state("profile_update")) is None
