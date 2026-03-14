"""Metamorphic tests for goal contract evaluation (Issue #44)."""

from __future__ import annotations

import pytest

from logic_brain import GoalContract, GoalContractStatus, evaluate_goal_contract


pytestmark = pytest.mark.metamorphic


def test_mr_gc01_equivalent_clause_formulations_preserve_outcome() -> None:
    context = {"sat": True, "unsat": False}
    contract_a = GoalContract(
        contract_id="a",
        invariants=("sat",),
        completion_criteria=("sat",),
    )
    contract_b = GoalContract(
        contract_id="b",
        invariants=("!unsat",),
        completion_criteria=("sat",),
    )

    result_a = evaluate_goal_contract(contract_a, strategy="safe", context=context)
    result_b = evaluate_goal_contract(contract_b, strategy="safe", context=context)

    assert result_a.status is result_b.status is GoalContractStatus.COMPLETED


def test_mr_gc02_clause_order_invariance() -> None:
    context = {"sat": True, "ready": True, "unsat": False}
    ordered = GoalContract(
        contract_id="ordered",
        preconditions=("sat", "ready"),
        invariants=("!unsat", "sat"),
        completion_criteria=("sat",),
    )
    reordered = GoalContract(
        contract_id="reordered",
        preconditions=("ready", "sat"),
        invariants=("sat", "!unsat"),
        completion_criteria=("sat",),
    )

    result_a = evaluate_goal_contract(ordered, strategy="safe", context=context)
    result_b = evaluate_goal_contract(reordered, strategy="safe", context=context)

    assert result_a.status == result_b.status
