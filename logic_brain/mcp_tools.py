"""Thin dict-in/dict-out wrappers for agent-facing logic tools."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib

from logic_brain.action_policy import ActionPolicyEngine, ActionPolicyRule
from logic_brain.assumptions import AssumptionKind, AssumptionSet
from logic_brain.certificate import certify
from logic_brain.counterfactual import CounterfactualPlanner
from logic_brain.mcp_session_store import (
    ExpiredSessionError,
    SessionLimitError,
    UnknownSessionError,
    Z3SessionStore,
)
from logic_brain.parser import ParseError, verify
from logic_brain.z3_session import Z3Session as SolverSession

ToolResult = dict[str, object]

_SESSION_STORE = Z3SessionStore()


def verify_argument(payload: Mapping[str, object]) -> ToolResult:
    """Verify a propositional argument and return certificate metadata."""
    try:
        data = _require_payload(payload)
        argument = _require_non_empty_str(data, "argument")

        result = verify(argument)
        certify(argument)
        return {
            "valid": result.valid,
            "rule": result.rule,
            "certificate_id": _certificate_id(argument),
            "explanation": result.explanation,
        }
    except Exception as exc:  # pragma: no cover - exercised via tests
        return _error_response(exc)


def check_assumptions(payload: Mapping[str, object]) -> ToolResult:
    """Check a set of assumptions for Z3-detectable contradictions."""
    try:
        data = _require_payload(payload)
        raw_assumptions = _require_list(data, "assumptions")
        variables = _optional_variables(data.get("variables"))

        assumptions = AssumptionSet()
        normalized: list[dict[str, str]] = []
        for item in raw_assumptions:
            assumption = _require_assumption(item)
            assumptions.add(
                assumption_id=assumption["id"],
                statement=assumption["statement"],
                kind=AssumptionKind(assumption["kind"]),
                source="mcp_tool",
            )
            normalized.append(assumption)

        consistency = assumptions.check_consistency_z3(variables=variables)
        return {
            "consistent": consistency.consistent,
            "conflict_ids": [] if consistency.consistent else _find_conflict_ids(normalized, variables),
            "explanation": _assumption_explanation(consistency.consistent, assumptions.active_statements()),
        }
    except Exception as exc:  # pragma: no cover - exercised via tests
        return _error_response(exc)


def counterfactual_branch(payload: Mapping[str, object]) -> ToolResult:
    """Evaluate multiple counterfactual branches against shared constraints."""
    try:
        data = _require_payload(payload)
        variables = _require_variable_specs(data, "variables")
        base_constraints = _require_str_list(data, "base_constraints")
        raw_branches = _require_dict(data, "branches")

        planner = CounterfactualPlanner()
        for name, spec in variables.items():
            sort, size = spec
            planner.declare(name, sort, size=size)
        for constraint in base_constraints:
            planner.assert_constraint(constraint)
        _validate_constraints(variables, base_constraints)

        branch_results: dict[str, dict[str, object | None]] = {}
        for branch_id, constraints_value in sorted(raw_branches.items()):
            if not isinstance(branch_id, str) or not branch_id:
                raise ValueError("Branch ids must be non-empty strings")
            constraints = _require_str_list_from_value(
                constraints_value,
                f"Branch '{branch_id}' must map to list[str] constraints",
            )
            branch = planner.branch(branch_id, additional_constraints=constraints)
            branch_results[branch_id] = {
                "satisfiable": branch.satisfiable,
                "status": branch.status,
                "model": None if branch.model is None else dict(branch.model),
            }

        return {"branches": branch_results}
    except Exception as exc:  # pragma: no cover - exercised via tests
        return _error_response(exc)


def z3_check(payload: Mapping[str, object]) -> ToolResult:
    """Run a satisfiability check over declared variables and constraints."""
    try:
        data = _require_payload(payload)
        variables = _require_variable_specs(data, "variables")
        constraints = _require_str_list(data, "constraints")

        session = SolverSession(track_unsat_core=True)
        for name, spec in variables.items():
            sort, size = spec
            session.declare(name, sort, size=size)
        for index, constraint in enumerate(constraints):
            session.assert_constraint(constraint, name=f"constraint_{index}")

        result = session.check()
        return {
            "satisfiable": result.satisfiable,
            "model": result.model,
            "unsat_core": result.unsat_core,
        }
    except Exception as exc:  # pragma: no cover - exercised via tests
        return _error_response(exc)


def z3_session(payload: Mapping[str, object]) -> ToolResult:
    """Manage a stateful Z3 session across multiple MCP tool calls."""
    try:
        data = _require_payload(payload)
        action = _require_non_empty_str(data, "action")
        session_id = _require_non_empty_str(data, "session_id")

        if action == "create":
            created = _SESSION_STORE.create(session_id)
            return {"session_id": created}
        if action == "destroy":
            _SESSION_STORE.destroy(session_id)
            return {"session_id": session_id, "destroyed": True}
        if action == "declare":
            variables = _require_variable_specs(data, "variables")
            declared = _SESSION_STORE.declare(session_id, variables)
            return {"session_id": session_id, "declared": declared}
        if action == "assert":
            constraints = _require_str_list(data, "constraints")
            added = _SESSION_STORE.assert_constraints(session_id, constraints)
            return {"session_id": session_id, "constraints_added": added}
        if action == "check":
            result = _SESSION_STORE.check(session_id)
            return {
                "session_id": session_id,
                "satisfiable": result.satisfiable,
                "model": result.model,
                "unsat_core": result.unsat_core,
            }
        if action == "push":
            depth = _SESSION_STORE.push(session_id)
            return {"session_id": session_id, "scope_depth": depth}
        if action == "pop":
            count = _optional_positive_int(data.get("count"), default=1)
            depth = _SESSION_STORE.pop(session_id, count=count)
            return {"session_id": session_id, "scope_depth": depth}

        raise ValueError(
            "Field 'action' must be one of: create, declare, assert, check, push, pop, destroy"
        )
    except Exception as exc:  # pragma: no cover - exercised via tests
        return _error_response(exc)


def check_policy(payload: Mapping[str, object]) -> ToolResult:
    """Evaluate an action against policy rules."""
    try:
        data = _require_payload(payload)
        raw_rules = _require_list(data, "rules")
        action = _require_bool_map(data, "action")

        engine = ActionPolicyEngine()
        for item in raw_rules:
            engine.add_rule(_build_policy_rule(item))

        result = engine.evaluate(action)
        violations = [
            {
                "policy_name": violation.policy_name,
                "severity": violation.severity,
                "message": violation.message,
                "triggered_fields": violation.triggered_fields,
            }
            for violation in result.violations
        ]
        return {
            "decision": result.decision.name,
            "violations": violations,
            "remediation_hints": result.remediation_hints,
        }
    except Exception as exc:  # pragma: no cover - exercised via tests
        return _error_response(exc)


def _require_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise TypeError("Tool input must be a dictionary")
    return {str(name): value for name, value in payload.items()}


def _require_dict(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Field '{key}' must be an object")
    return {str(name): item for name, item in value.items()}


def _require_list(payload: dict[str, object], key: str) -> list[object]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Field '{key}' must be a list")
    return value


def _require_non_empty_str(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{key}' must be a non-empty string")
    return value


def _require_str_list(payload: dict[str, object], key: str) -> list[str]:
    return _require_str_list_from_value(payload.get(key), f"Field '{key}' must be a list of strings")


def _require_str_list_from_value(value: object, message: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(message)
    return list(value)


def _optional_variables(value: object) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("Field 'variables' must be an object")
    normalized: dict[str, str] = {}
    for name, sort in value.items():
        if not isinstance(name, str) or not name:
            raise ValueError("Variable names must be non-empty strings")
        if not isinstance(sort, str) or not sort:
            raise ValueError(f"Variable '{name}' must declare a non-empty sort string")
        normalized[name] = sort
    return normalized


def _require_variable_specs(
    payload: dict[str, object],
    key: str,
) -> dict[str, tuple[str, int | None]]:
    raw_variables = _require_dict(payload, key)
    normalized: dict[str, tuple[str, int | None]] = {}
    for name, spec in sorted(raw_variables.items()):
        if not name:
            raise ValueError("Variable names must be non-empty strings")
        normalized[name] = _normalize_variable_spec(name, spec)
    return normalized


def _normalize_variable_spec(name: str, spec: object) -> tuple[str, int | None]:
    if isinstance(spec, str):
        return spec, None
    if not isinstance(spec, dict):
        raise ValueError(f"Variable '{name}' must be a sort string or object")

    sort = spec.get("sort")
    if not isinstance(sort, str) or not sort:
        raise ValueError(f"Variable '{name}' requires a non-empty 'sort' string")

    size = spec.get("size")
    if size is not None and not isinstance(size, int):
        raise ValueError(f"Variable '{name}' field 'size' must be an integer")

    return sort, size


def _validate_constraints(
    variables: dict[str, tuple[str, int | None]],
    constraints: list[str],
) -> None:
    session = SolverSession()
    for name, (sort, size) in variables.items():
        session.declare(name, sort, size=size)
    for constraint in constraints:
        session.assert_constraint(constraint)


def _require_assumption(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("Assumption entries must be objects")

    assumption_id = value.get("id")
    statement = value.get("statement")
    kind = value.get("kind")

    if not isinstance(assumption_id, str) or not assumption_id:
        raise ValueError("Assumption field 'id' must be a non-empty string")
    if not isinstance(statement, str) or not statement:
        raise ValueError("Assumption field 'statement' must be a non-empty string")
    if not isinstance(kind, str) or not kind:
        raise ValueError("Assumption field 'kind' must be a non-empty string")
    if kind not in {item.value for item in AssumptionKind}:
        raise ValueError("Assumption field 'kind' must be one of: fact, assumption, hypothesis")

    return {"id": assumption_id, "statement": statement, "kind": kind}


def _find_conflict_ids(
    assumptions: list[dict[str, str]],
    variables: dict[str, str] | None,
) -> list[str]:
    if len(assumptions) <= 1:
        return [item["id"] for item in assumptions]

    conflict_ids: list[str] = []
    for candidate in assumptions:
        reduced = [item for item in assumptions if item["id"] != candidate["id"]]
        reduced_set = AssumptionSet()
        for item in reduced:
            reduced_set.add(
                assumption_id=item["id"],
                statement=item["statement"],
                kind=AssumptionKind(item["kind"]),
                source="mcp_tool",
            )
        if reduced_set.check_consistency_z3(variables=variables).consistent:
            conflict_ids.append(candidate["id"])

    return conflict_ids or [item["id"] for item in assumptions]


def _assumption_explanation(consistent: bool, statements: list[str]) -> str:
    if consistent:
        return f"All {len(statements)} active assumptions are jointly satisfiable."
    return "The active assumptions contain a contradiction under the supplied variable declarations."


def _require_bool_map(payload: dict[str, object], key: str) -> dict[str, bool]:
    raw = _require_dict(payload, key)
    normalized: dict[str, bool] = {}
    for name, value in raw.items():
        if not isinstance(value, bool):
            raise ValueError(f"Action field '{name}' must be a boolean")
        normalized[name] = value
    return normalized


def _optional_positive_int(value: object, default: int) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or value < 1:
        raise ValueError("Field 'count' must be an integer >= 1")
    return value


def _build_policy_rule(value: object) -> ActionPolicyRule:
    if not isinstance(value, dict):
        raise ValueError("Policy rule entries must be objects")

    name = value.get("name")
    severity = value.get("severity")
    message = value.get("message")
    when_true = value.get("when_true", [])
    when_false = value.get("when_false", [])

    if not isinstance(name, str) or not name:
        raise ValueError("Policy field 'name' must be a non-empty string")
    if not isinstance(severity, str) or not severity:
        raise ValueError("Policy field 'severity' must be a non-empty string")
    if not isinstance(message, str) or not message:
        raise ValueError("Policy field 'message' must be a non-empty string")

    return ActionPolicyRule(
        name=name,
        severity=severity,
        message=message,
        when_true=tuple(
            _require_str_list_from_value(
                when_true,
                "Policy field 'when_true' must be a list of strings",
            )
        ),
        when_false=tuple(
            _require_str_list_from_value(
                when_false,
                "Policy field 'when_false' must be a list of strings",
            )
        ),
    )


def _certificate_id(serialized_certificate: str) -> str:
    return hashlib.sha256(serialized_certificate.encode("utf-8")).hexdigest()


def _error_response(exc: Exception) -> ToolResult:
    if isinstance(exc, UnknownSessionError):
        return {"error": "Unknown session", "details": str(exc)}
    if isinstance(exc, ExpiredSessionError):
        return {"error": "Expired session", "details": str(exc)}
    if isinstance(exc, SessionLimitError):
        return {"error": "Session limit reached", "details": str(exc)}
    if isinstance(exc, (ParseError, TypeError, ValueError)):
        return {"error": "Invalid input", "details": str(exc)}
    return {"error": exc.__class__.__name__, "details": str(exc)}
