"""Metamorphic tests for causal/temporal belief graph (Issue #46)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from logic_brain import BeliefEdgeType, BeliefGraph


pytestmark = pytest.mark.metamorphic


def test_mr_bg01_support_order_invariance() -> None:
    ordered = BeliefGraph()
    ordered.add_belief("a", "Root")
    ordered.add_belief("b", "Mid")
    ordered.add_belief("c", "Goal")
    ordered.add_edge("a", "b", BeliefEdgeType.SUPPORTS)
    ordered.add_edge("b", "c", BeliefEdgeType.DERIVED_FROM)

    reordered = BeliefGraph()
    reordered.add_belief("a", "Root")
    reordered.add_belief("b", "Mid")
    reordered.add_belief("c", "Goal")
    reordered.add_edge("b", "c", BeliefEdgeType.DERIVED_FROM)
    reordered.add_edge("a", "b", BeliefEdgeType.SUPPORTS)

    assert ordered.minimal_support_set("c") == reordered.minimal_support_set("c")


def test_mr_bg02_temporal_shift_consistency() -> None:
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    shift = timedelta(hours=3)

    graph_a = BeliefGraph()
    graph_a.add_belief("a", "Evidence", valid_from=base_time, ttl_seconds=60)
    graph_a.add_belief("b", "Claim", valid_from=base_time)
    graph_a.add_edge("a", "b", BeliefEdgeType.SUPPORTS)
    stale_a = graph_a.stale_dependencies(at_time=base_time + timedelta(minutes=5))

    graph_b = BeliefGraph()
    graph_b.add_belief("a", "Evidence", valid_from=base_time + shift, ttl_seconds=60)
    graph_b.add_belief("b", "Claim", valid_from=base_time + shift)
    graph_b.add_edge("a", "b", BeliefEdgeType.SUPPORTS)
    stale_b = graph_b.stale_dependencies(at_time=base_time + shift + timedelta(minutes=5))

    assert stale_a == stale_b
