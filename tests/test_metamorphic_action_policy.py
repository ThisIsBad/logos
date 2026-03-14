"""Metamorphic tests for action policy enforcement (Issue #35)."""

from __future__ import annotations

import pytest

from logic_brain import ActionPolicyEngine, ActionPolicyRule, PolicyDecision


pytestmark = pytest.mark.metamorphic


def _decision_rank(decision: PolicyDecision) -> int:
    if decision is PolicyDecision.ALLOW:
        return 0
    if decision is PolicyDecision.REVIEW_REQUIRED:
        return 1
    return 2


def test_mr_ap01_removing_policy_cannot_introduce_new_violations() -> None:
    full = ActionPolicyEngine(
        [
            ActionPolicyRule(
                name="rule_a",
                severity="error",
                message="A",
                when_true=("a",),
            ),
            ActionPolicyRule(
                name="rule_b",
                severity="warning",
                message="B",
                when_true=("b",),
            ),
        ]
    )
    reduced = ActionPolicyEngine(
        [
            ActionPolicyRule(
                name="rule_a",
                severity="error",
                message="A",
                when_true=("a",),
            )
        ]
    )

    action = {"a": True, "b": True}
    full_result = full.evaluate(action)
    reduced_result = reduced.evaluate(action)

    assert len(reduced_result.violations) <= len(full_result.violations)
    assert _decision_rank(reduced_result.decision) <= _decision_rank(full_result.decision)


def test_mr_ap02_evaluation_order_does_not_change_decision() -> None:
    ordered = ActionPolicyEngine(
        [
            ActionPolicyRule(
                name="rule_a",
                severity="warning",
                message="A",
                when_true=("a",),
            ),
            ActionPolicyRule(
                name="rule_b",
                severity="error",
                message="B",
                when_true=("b",),
            ),
        ]
    )
    reversed_engine = ActionPolicyEngine(
        [
            ActionPolicyRule(
                name="rule_b",
                severity="error",
                message="B",
                when_true=("b",),
            ),
            ActionPolicyRule(
                name="rule_a",
                severity="warning",
                message="A",
                when_true=("a",),
            ),
        ]
    )

    action = {"a": True, "b": True}

    assert ordered.evaluate(action).decision is reversed_engine.evaluate(action).decision
