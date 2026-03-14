"""Tests for counterfactual planning (Issue #34)."""

from __future__ import annotations

import pytest

from logic_brain import CounterfactualPlanner


def _new_planner() -> CounterfactualPlanner:
    planner = CounterfactualPlanner()
    planner.declare("x", "Int")
    planner.assert_constraint("x > 0")
    return planner


def test_sibling_branches_are_isolated() -> None:
    planner = _new_planner()

    branch_unsat = planner.branch("b1", additional_constraints=["x < 0"])
    branch_sat = planner.branch("b2", additional_constraints=["x < 10"])

    assert branch_unsat.status == "unsat"
    assert branch_sat.status == "sat"


def test_branch_from_parent_inherits_state_without_mutating_parent() -> None:
    planner = _new_planner()

    parent = planner.branch("parent", additional_constraints=["x < 10"])
    child = planner.branch("child", parent_id="parent", additional_constraints=["x > 100"])
    replay_parent = planner.replay("parent")

    assert parent.status == "sat"
    assert child.status == "unsat"
    assert replay_parent.status == "sat"


def test_branch_replay_is_deterministic() -> None:
    planner = _new_planner()
    branch = planner.branch("b1", additional_constraints=["x < 10"])

    replay_a = planner.replay("b1")
    replay_b = planner.replay("b1")

    assert replay_a.status == branch.status == replay_b.status
    assert replay_a.satisfiable is branch.satisfiable is replay_b.satisfiable


def test_branch_certificates_are_independently_reverifiable() -> None:
    planner = _new_planner()
    planner.branch("sat_branch", additional_constraints=["x < 10"])
    planner.branch("unsat_branch", additional_constraints=["x < 0"])

    assert planner.verify_branch_certificate("sat_branch") is True
    assert planner.verify_branch_certificate("unsat_branch") is True


def test_scoring_hooks_attach_scores() -> None:
    planner = _new_planner()
    branch = planner.branch("b1", additional_constraints=["x < 10"])

    def sat_score(target) -> float:  # type: ignore[no-untyped-def]
        return 1.0 if target.satisfiable is True else 0.0

    scored = planner.score_branch("b1", {"sat_score": sat_score})

    assert scored is branch
    assert scored.scores["sat_score"] == 1.0


def test_unknown_parent_branch_rejected() -> None:
    planner = _new_planner()

    with pytest.raises(ValueError, match="Unknown parent branch"):
        planner.branch("b1", parent_id="missing", additional_constraints=["x < 10"])
