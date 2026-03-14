"""Metamorphic tests for counterfactual planner (Issue #34)."""

from __future__ import annotations

import pytest

from logic_brain import CounterfactualPlanner


pytestmark = pytest.mark.metamorphic


def _build_planner() -> CounterfactualPlanner:
    planner = CounterfactualPlanner()
    planner.declare("x", "Int")
    planner.assert_constraint("x > 0")
    return planner


def test_mr_cp01_branch_creation_order_preserves_classification() -> None:
    first = _build_planner()
    first.branch("sat", additional_constraints=["x < 10"])
    first.branch("unsat", additional_constraints=["x < 0"])

    second = _build_planner()
    second.branch("unsat", additional_constraints=["x < 0"])
    second.branch("sat", additional_constraints=["x < 10"])

    assert first.get_branch("sat").status == second.get_branch("sat").status
    assert first.get_branch("unsat").status == second.get_branch("unsat").status


def test_mr_cp02_repeated_replay_preserves_classification() -> None:
    planner = _build_planner()
    branch = planner.branch("sat", additional_constraints=["x < 10"])

    replay_a = planner.replay("sat")
    replay_b = planner.replay("sat")

    assert replay_a.status == replay_b.status == branch.status
    assert replay_a.satisfiable is replay_b.satisfiable is branch.satisfiable
