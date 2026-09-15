"""Tests for graph.construct's compiled_graph."""

import pytest

from graph.construct import compiled_graph


def test_compiled_graph_builds_without_error():
    assert compiled_graph is not None


def test_compiled_graph_has_expected_nodes():
    """orchestrator, profile_router, parse_profile, create_profile,
    calculate_crs, evaluate_express_entry, create_advice."""
    nodes = set(compiled_graph.get_graph().nodes)
    expected = {
        "orchestrator",
        "profile_router",
        "parse_profile",
        "create_profile",
        "calculate_crs",
        "evaluate_express_entry",
        "create_advice",
    }
    assert expected.issubset(nodes)
