"""Tests for causal and temporal belief graph (Issue #46)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from logic_brain import AssumptionKind, AssumptionSet, BeliefEdgeType, BeliefGraph, UncertaintyCalibrator
from logic_brain.uncertainty import ConfidenceLevel


def test_minimal_support_set_traces_to_root_supports() -> None:
    graph = BeliefGraph()
    graph.add_belief("a", "Root fact")
    graph.add_belief("b", "Intermediate")
    graph.add_belief("c", "Conclusion")
    graph.add_edge("a", "b", BeliefEdgeType.SUPPORTS)
    graph.add_edge("b", "c", BeliefEdgeType.DERIVED_FROM)

    assert graph.minimal_support_set("c") == ("a",)


def test_stale_dependencies_are_detected_deterministically() -> None:
    graph = BeliefGraph()
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    graph.add_belief("a", "Old evidence", valid_from=t0, ttl_seconds=60)
    graph.add_belief("b", "Current claim", valid_from=t0)
    graph.add_edge("a", "b", BeliefEdgeType.SUPPORTS)

    stale = graph.stale_dependencies(at_time=t0 + timedelta(seconds=120))
    assert stale == ("a",)


def test_contradiction_frontier_and_explanation_are_explicit() -> None:
    graph = BeliefGraph()
    graph.add_belief("r1", "Base support left")
    graph.add_belief("r2", "Base support right")
    graph.add_belief("left", "P")
    graph.add_belief("right", "~P")
    graph.add_edge("r1", "left", BeliefEdgeType.SUPPORTS)
    graph.add_edge("r2", "right", BeliefEdgeType.SUPPORTS)
    graph.add_edge("left", "right", BeliefEdgeType.CONTRADICTS)

    frontier = graph.contradiction_frontier()
    explanation = graph.explain_contradiction("left", "right")

    assert frontier == (("left", "right"),)
    assert explanation.left_support_path == ("left", "r1")
    assert explanation.right_support_path == ("right", "r2")


def test_z3_contradiction_detection_finds_real_contradictions() -> None:
    graph = BeliefGraph()
    graph.add_belief("a", "x > 0")
    graph.add_belief("b", "x < 0")
    graph.add_belief("c", "x < 100")

    contradictions = graph.detect_contradictions_z3(variables={"x": "Int"})

    assert contradictions == (("a", "b"),)
    assert graph.contradiction_frontier() == (("a", "b"),)


def test_z3_contradiction_detection_with_no_contradictions() -> None:
    graph = BeliefGraph()
    graph.add_belief("a", "x > 0")
    graph.add_belief("b", "x < 100")

    contradictions = graph.detect_contradictions_z3(variables={"x": "Int"})

    assert contradictions == ()


def test_integration_hooks_with_assumptions_and_uncertainty() -> None:
    assumptions = AssumptionSet()
    assumptions.add("a1", "x > 0", AssumptionKind.ASSUMPTION, "sensor")

    graph = BeliefGraph()
    ingested = graph.ingest_assumptions(assumptions)
    level = graph.calibrate_confidence(
        belief_id="a1",
        calibrator=UncertaintyCalibrator(),
        verified=True,
        evidence_count=2,
    )

    assert ingested == ("a1",)
    assert level is ConfidenceLevel.CERTAIN
    assert graph.confidence("a1") is ConfidenceLevel.CERTAIN
