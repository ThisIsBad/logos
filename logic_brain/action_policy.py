"""Deterministic pre-action policy enforcement."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
import re

from logic_brain.schema_utils import (
    load_json_object,
    require_dict,
    require_list,
    require_list_of_str,
    require_str,
)
from logic_brain.z3_session import CheckResult

SCHEMA_VERSION = "1.0"


class PolicyDecision(Enum):
    """Policy decision outcomes for a proposed action."""

    ALLOW = "allow"
    REVIEW_REQUIRED = "review_required"
    BLOCK = "block"


@dataclass(frozen=True)
class ActionPolicyRule:
    """One action policy rule with explicit trigger conditions."""

    name: str
    severity: str
    message: str
    when_true: tuple[str, ...] = ()
    when_false: tuple[str, ...] = ()

    def validate(self) -> None:
        """Validate policy schema constraints."""
        if not self.name:
            raise ValueError("Policy rule name cannot be empty")
        if self.severity not in {"error", "warning"}:
            raise ValueError("Policy severity must be 'error' or 'warning'")
        if not self.message:
            raise ValueError("Policy rule message cannot be empty")

    def is_triggered(self, action: dict[str, bool]) -> bool:
        """Return True if the action violates this rule."""
        return all(action.get(field, False) for field in self.when_true) and all(
            not action.get(field, False) for field in self.when_false
        )


@dataclass(frozen=True)
class PolicyViolationEvidence:
    """Structured policy violation evidence."""

    policy_name: str
    severity: str
    message: str
    triggered_fields: list[str]


@dataclass(frozen=True)
class ActionPolicyResult:
    """Evaluation result for an action proposal."""

    decision: PolicyDecision
    violations: list[PolicyViolationEvidence]
    remediation_hints: list[str]


class ActionPolicyEngine:
    """Evaluate actions against deterministic policy rules."""

    def __init__(self, rules: list[ActionPolicyRule] | None = None) -> None:
        self._rules: list[ActionPolicyRule] = []
        for rule in rules or []:
            self.add_rule(rule)

    def add_rule(self, rule: ActionPolicyRule) -> None:
        """Register a policy rule."""
        rule.validate()
        if any(existing.name == rule.name for existing in self._rules):
            raise ValueError(f"Policy rule '{rule.name}' already exists")
        self._rules.append(rule)

    def evaluate(self, action: dict[str, bool]) -> ActionPolicyResult:
        """Evaluate one action and return deterministic enforcement result."""
        violations: list[PolicyViolationEvidence] = []

        for rule in self._rules:
            if rule.is_triggered(action):
                triggered_fields = list(rule.when_true) + list(rule.when_false)
                violations.append(
                    PolicyViolationEvidence(
                        policy_name=rule.name,
                        severity=rule.severity,
                        message=rule.message,
                        triggered_fields=triggered_fields,
                    )
                )

        decision = _decision_from_violations(violations)
        remediation_hints = _build_remediation_hints(violations)
        return ActionPolicyResult(
            decision=decision,
            violations=violations,
            remediation_hints=remediation_hints,
        )

    def check_policy_consistency_z3(
        self,
        variables: dict[str, str] | None = None,
        constraints: list[str] | None = None,
        timeout_ms: int = 30000,
    ) -> tuple[tuple[str, str], ...]:
        """Return rule pairs whose trigger conditions are jointly UNSAT in Z3.

        Mapping semantics:
        - every name in ``when_true`` becomes a boolean literal
        - every name in ``when_false`` becomes a negated boolean literal
        - a rule triggers exactly when the conjunction of those literals holds

        A pair is reported as contradictory when Z3 proves there is no boolean
        assignment, optionally under the supplied extra constraints, that makes
        both rules trigger at the same time.
        """
        contradictory_pairs: set[tuple[str, str]] = set()

        for index, left_rule in enumerate(self._rules):
            for right_rule in self._rules[index + 1 :]:
                result = _check_policy_formulas(
                    formulas=[_rule_trigger_formula(left_rule), _rule_trigger_formula(right_rule)],
                    rules=[left_rule, right_rule],
                    variables=variables,
                    constraints=constraints,
                    timeout_ms=timeout_ms,
                )
                if result.satisfiable is False:
                    contradictory_pairs.add((left_rule.name, right_rule.name))

        return tuple(sorted(contradictory_pairs))

    def check_policy_subsumption_z3(
        self,
        rule_a: ActionPolicyRule,
        rule_b: ActionPolicyRule,
        variables: dict[str, str] | None = None,
        constraints: list[str] | None = None,
        timeout_ms: int = 30000,
    ) -> bool:
        """Return whether ``rule_a`` is strictly more restrictive than ``rule_b``.

        The comparison is over rule trigger sets. ``rule_a`` subsumes ``rule_b``
        when every assignment that triggers ``rule_b`` also triggers ``rule_a``,
        and there exists at least one assignment that triggers ``rule_a`` without
        triggering ``rule_b``.
        """
        rule_a.validate()
        rule_b.validate()

        formula_a = _rule_trigger_formula(rule_a)
        formula_b = _rule_trigger_formula(rule_b)

        implication_check = _check_policy_formulas(
            formulas=[formula_b, f"not ({formula_a})"],
            rules=[rule_a, rule_b],
            variables=variables,
            constraints=constraints,
            timeout_ms=timeout_ms,
        )
        if implication_check.satisfiable is not False:
            return False

        strictness_check = _check_policy_formulas(
            formulas=[formula_a, f"not ({formula_b})"],
            rules=[rule_a, rule_b],
            variables=variables,
            constraints=constraints,
            timeout_ms=timeout_ms,
        )
        return strictness_check.satisfiable is True

    def to_dict(self) -> dict[str, object]:
        """Serialize policy set to dictionary."""
        return {
            "schema_version": SCHEMA_VERSION,
            "rules": [
                {
                    "name": rule.name,
                    "severity": rule.severity,
                    "message": rule.message,
                    "when_true": list(rule.when_true),
                    "when_false": list(rule.when_false),
                }
                for rule in self._rules
            ],
        }

    def to_json(self) -> str:
        """Serialize policy set to JSON."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ActionPolicyEngine":
        """Deserialize policy set from dictionary."""
        schema_version = payload.get("schema_version")
        rules = require_list(
            payload.get("rules"),
            "Action policy payload requires list field 'rules'",
        )

        if schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported action-policy schema version '{schema_version}'")

        parsed_rules: list[ActionPolicyRule] = []
        for item in rules:
            item_dict = require_dict(item, "Policy rule entries must be objects")

            name = require_str(item_dict.get("name"), "Policy field 'name' must be a string")
            severity = require_str(item_dict.get("severity"), "Policy field 'severity' must be a string")
            message = require_str(item_dict.get("message"), "Policy field 'message' must be a string")
            when_true = require_list_of_str(
                item_dict.get("when_true", []),
                "Policy field 'when_true' must be a list[str]",
            )
            when_false = require_list_of_str(
                item_dict.get("when_false", []),
                "Policy field 'when_false' must be a list[str]",
            )

            parsed_rules.append(
                ActionPolicyRule(
                    name=name,
                    severity=severity,
                    message=message,
                    when_true=tuple(when_true),
                    when_false=tuple(when_false),
                )
            )

        return cls(parsed_rules)

    @classmethod
    def from_json(cls, raw_json: str) -> "ActionPolicyEngine":
        """Deserialize policy set from JSON string."""
        payload = load_json_object(
            raw_json,
            invalid_error="Invalid action-policy JSON",
            object_error="Action-policy JSON must be an object",
        )
        return cls.from_dict(payload)

    @classmethod
    def from_legacy_policies(cls, legacy_rules: list[dict[str, object]]) -> "ActionPolicyEngine":
        """Compatibility loader for simple legacy policy dictionaries."""
        rules: list[ActionPolicyRule] = []
        for item in legacy_rules:
            name = require_str(item.get("name"), "Legacy policy field 'name' must be a string")
            severity = require_str(item.get("severity"), "Legacy policy field 'severity' must be a string")
            message = require_str(item.get("message"), "Legacy policy field 'message' must be a string")
            when_true = require_list_of_str(
                item.get("when_true", []),
                "Legacy policy field 'when_true' must be a list[str]",
            )
            when_false = require_list_of_str(
                item.get("when_false", []),
                "Legacy policy field 'when_false' must be a list[str]",
            )

            rules.append(
                ActionPolicyRule(
                    name=name,
                    severity=severity,
                    message=message,
                    when_true=tuple(when_true),
                    when_false=tuple(when_false),
                )
            )

        return cls(rules)


def _decision_from_violations(violations: list[PolicyViolationEvidence]) -> PolicyDecision:
    if any(v.severity == "error" for v in violations):
        return PolicyDecision.BLOCK
    if any(v.severity == "warning" for v in violations):
        return PolicyDecision.REVIEW_REQUIRED
    return PolicyDecision.ALLOW


def _build_remediation_hints(violations: list[PolicyViolationEvidence]) -> list[str]:
    return [
        f"Resolve policy '{violation.policy_name}': {violation.message}"
        for violation in violations
    ]


def _check_policy_formulas(
    formulas: list[str],
    rules: list[ActionPolicyRule],
    variables: dict[str, str] | None,
    constraints: list[str] | None,
    timeout_ms: int,
) -> CheckResult:
    from logic_brain.z3_session import Z3Session

    session = Z3Session(timeout_ms=timeout_ms)
    _declare_policy_variables(session, rules=rules, variables=variables, constraints=constraints)

    for constraint in constraints or []:
        session.assert_constraint(constraint)
    for formula in formulas:
        session.assert_constraint(formula)

    return session.check()


def _declare_policy_variables(
    session: object,
    rules: list[ActionPolicyRule],
    variables: dict[str, str] | None,
    constraints: list[str] | None,
) -> None:
    declare = getattr(session, "declare")
    if not callable(declare):
        raise ValueError("session object must provide declare()")

    rule_fields = {field for rule in rules for field in rule.when_true + rule.when_false}
    declared_sorts = dict(variables or {})

    for field in sorted(rule_fields):
        explicit_sort = declared_sorts.get(field)
        if explicit_sort is not None and explicit_sort.upper() != "BOOL":
            raise ValueError(f"Policy field '{field}' must use Bool sort for Z3 checks")

    for var_name in sorted(_infer_constraint_identifiers(constraints or [])):
        declared_sorts.setdefault(var_name, "Bool")
    for field in sorted(rule_fields):
        declared_sorts.setdefault(field, "Bool")

    for var_name, sort in sorted(declared_sorts.items()):
        declare(var_name, sort)


def _infer_constraint_identifiers(constraints: list[str]) -> set[str]:
    identifiers: set[str] = set()
    for constraint in constraints:
        identifiers.update(_IDENTIFIER_PATTERN.findall(constraint))
    return {name for name in identifiers if name not in _RESERVED_IDENTIFIERS}


def _rule_trigger_formula(rule: ActionPolicyRule) -> str:
    parts = [field for field in rule.when_true]
    parts.extend(f"not ({field})" for field in rule.when_false)
    if not parts:
        return "True"
    return " and ".join(f"({part})" for part in parts)


_IDENTIFIER_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_RESERVED_IDENTIFIERS = {"True", "False", "and", "or", "not"}
