"""Metamorphic tests for assumption state kernel (Issue #33)."""

from __future__ import annotations

import pytest

from logic_brain import AssumptionKind, AssumptionSet


pytestmark = pytest.mark.metamorphic


def _checker(statements: list[str]) -> bool:
    return not ("x > 0" in statements and "x < 0" in statements)


def test_mr_a01_assumption_order_invariance_for_consistency() -> None:
    ordered = AssumptionSet()
    ordered.add("a1", "x > 0", AssumptionKind.ASSUMPTION, "test")
    ordered.add("a2", "x < 0", AssumptionKind.ASSUMPTION, "test")

    reversed_set = AssumptionSet()
    reversed_set.add("a2", "x < 0", AssumptionKind.ASSUMPTION, "test")
    reversed_set.add("a1", "x > 0", AssumptionKind.ASSUMPTION, "test")

    assert ordered.check_consistency(_checker).consistent is reversed_set.check_consistency(_checker).consistent


def test_mr_a02_redundant_retraction_is_idempotent() -> None:
    assumptions = AssumptionSet()
    assumptions.add("a1", "x > 0", AssumptionKind.ASSUMPTION, "test")

    first = assumptions.retract("a1")
    second = assumptions.retract("a1")
    third = assumptions.retract("a1")

    assert first.status == second.status == third.status
