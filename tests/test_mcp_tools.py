"""Tests for MCP tool wrappers (Issues #55, #56)."""

from __future__ import annotations

from logic_brain.mcp_tools import (
    check_assumptions,
    check_policy,
    counterfactual_branch,
    verify_argument,
    z3_check,
)


def test_verify_argument_valid_modus_ponens() -> None:
    result = verify_argument({"argument": "P -> Q, P |- Q"})

    assert result["valid"] is True
    assert result["rule"] == "Modus Ponens"
    assert isinstance(result["certificate_id"], str)
    assert result["explanation"]


def test_verify_argument_invalid_argument() -> None:
    result = verify_argument({"argument": "P -> Q, Q |- P"})

    assert result["valid"] is False
    assert "explanation" in result


def test_verify_argument_returns_structured_error_for_malformed_input() -> None:
    result = verify_argument({"argument": "P -> Q, P -| Q"})

    assert result["error"] == "Invalid input"
    assert isinstance(result["details"], str)


def test_verify_argument_requires_argument_key() -> None:
    result = verify_argument({})

    assert result == {
        "error": "Invalid input",
        "details": "Field 'argument' must be a non-empty string",
    }


def test_check_assumptions_reports_consistent_set() -> None:
    result = check_assumptions(
        {
            "assumptions": [
                {"id": "a1", "statement": "x > 0", "kind": "assumption"},
                {"id": "a2", "statement": "x < 10", "kind": "fact"},
            ],
            "variables": {"x": "Int"},
        }
    )

    assert result == {
        "consistent": True,
        "conflict_ids": [],
        "explanation": "All 2 active assumptions are jointly satisfiable.",
    }


def test_check_assumptions_reports_conflicts() -> None:
    result = check_assumptions(
        {
            "assumptions": [
                {"id": "a1", "statement": "x > 0", "kind": "assumption"},
                {"id": "a2", "statement": "x < 0", "kind": "hypothesis"},
            ],
            "variables": {"x": "Int"},
        }
    )

    assert result["consistent"] is False
    assert result["conflict_ids"] == ["a1", "a2"]
    assert "contradiction" in str(result["explanation"]).lower()


def test_check_assumptions_empty_list_is_vacuously_consistent() -> None:
    result = check_assumptions({"assumptions": []})

    assert result == {
        "consistent": True,
        "conflict_ids": [],
        "explanation": "All 0 active assumptions are jointly satisfiable.",
    }


def test_check_assumptions_rejects_missing_fields() -> None:
    result = check_assumptions(
        {
            "assumptions": [
                {"id": "a1", "kind": "assumption"},
            ]
        }
    )

    assert result["error"] == "Invalid input"
    assert "statement" in str(result["details"])


def test_check_assumptions_rejects_invalid_kind() -> None:
    result = check_assumptions(
        {
            "assumptions": [
                {"id": "a1", "statement": "x > 0", "kind": "belief"},
            ]
        }
    )

    assert result["error"] == "Invalid input"
    assert "fact, assumption, hypothesis" in str(result["details"])


def test_counterfactual_branch_classifies_sat_and_unsat_branches() -> None:
    result = counterfactual_branch(
        {
            "variables": {"x": "Int"},
            "base_constraints": ["x > 0"],
            "branches": {
                "sat_branch": ["x < 10"],
                "unsat_branch": ["x < 0"],
            },
        }
    )

    branches = result["branches"]
    assert isinstance(branches, dict)

    sat_branch = branches["sat_branch"]
    assert sat_branch["satisfiable"] is True
    assert sat_branch["status"] == "sat"
    assert isinstance(sat_branch["model"], dict)
    assert "x" in sat_branch["model"]

    unsat_branch = branches["unsat_branch"]
    assert unsat_branch == {"satisfiable": False, "status": "unsat", "model": None}


def test_counterfactual_branch_handles_empty_branches() -> None:
    result = counterfactual_branch(
        {
            "variables": {"x": "Int"},
            "base_constraints": ["x > 0"],
            "branches": {},
        }
    )

    assert result == {"branches": {}}


def test_counterfactual_branch_rejects_invalid_variable_declarations() -> None:
    result = counterfactual_branch(
        {
            "variables": {"x": 1},
            "base_constraints": [],
            "branches": {},
        }
    )

    assert result["error"] == "Invalid input"
    assert "Variable 'x'" in str(result["details"])


def test_counterfactual_branch_rejects_malformed_constraints() -> None:
    result = counterfactual_branch(
        {
            "variables": {"x": "Int"},
            "base_constraints": ["x >"],
            "branches": {},
        }
    )

    assert result["error"] == "Invalid input"
    assert "Failed to parse constraint" in str(result["details"])


def test_z3_check_returns_model_for_sat_constraints() -> None:
    result = z3_check(
        {
            "variables": {"x": "Int"},
            "constraints": ["x > 0", "x < 10"],
        }
    )

    assert result["satisfiable"] is True
    assert isinstance(result["model"], dict)
    assert result["unsat_core"] is None


def test_z3_check_reports_unsat_constraints() -> None:
    result = z3_check(
        {
            "variables": {"x": "Int"},
            "constraints": ["x > 0", "x < 0"],
        }
    )

    assert result["satisfiable"] is False
    assert result["model"] is None
    assert isinstance(result["unsat_core"], list)


def test_z3_check_empty_constraints_are_sat() -> None:
    result = z3_check({"variables": {}, "constraints": []})

    assert result == {"satisfiable": True, "model": {}, "unsat_core": None}


def test_z3_check_rejects_invalid_constraint_syntax() -> None:
    result = z3_check(
        {
            "variables": {"x": "Int"},
            "constraints": ["x >"],
        }
    )

    assert result["error"] == "Invalid input"
    assert "Failed to parse constraint" in str(result["details"])


def test_z3_check_rejects_undeclared_variables() -> None:
    result = z3_check(
        {
            "variables": {},
            "constraints": ["x > 0"],
        }
    )

    assert result["error"] == "Invalid input"
    assert "Variable 'x' not declared" in str(result["details"])


def test_check_policy_blocks_error_violations() -> None:
    result = check_policy(
        {
            "rules": [
                {
                    "name": "test_coverage",
                    "severity": "error",
                    "message": "Public API changes require tests",
                    "when_true": ["target_is_public_api"],
                    "when_false": ["has_tests"],
                }
            ],
            "action": {"target_is_public_api": True, "has_tests": False},
        }
    )

    assert result["decision"] == "BLOCK"
    violations = result["violations"]
    assert isinstance(violations, list)
    assert len(violations) == 1
    assert result["remediation_hints"]


def test_check_policy_returns_review_required_for_warning_only() -> None:
    result = check_policy(
        {
            "rules": [
                {
                    "name": "dependency_review",
                    "severity": "warning",
                    "message": "New dependencies require review",
                    "when_true": ["adds_dependency"],
                }
            ],
            "action": {"adds_dependency": True},
        }
    )

    assert result["decision"] == "REVIEW_REQUIRED"
    violations = result["violations"]
    assert isinstance(violations, list)
    assert len(violations) == 1


def test_check_policy_allows_clean_action_and_empty_rules() -> None:
    result = check_policy({"rules": [], "action": {"adds_dependency": False}})

    assert result == {
        "decision": "ALLOW",
        "violations": [],
        "remediation_hints": [],
    }


def test_check_policy_rejects_invalid_rule_schema() -> None:
    result = check_policy(
        {
            "rules": [
                {
                    "name": "bad_rule",
                    "severity": "fatal",
                    "message": "Bad severity",
                }
            ],
            "action": {},
        }
    )

    assert result["error"] == "Invalid input"
    assert "severity" in str(result["details"])


def test_all_tools_return_structured_errors_for_bad_payload_types() -> None:
    tools = [
        verify_argument,
        check_assumptions,
        counterfactual_branch,
        z3_check,
        check_policy,
    ]

    for tool in tools:
        result = tool("not-a-dict")  # type: ignore[arg-type]
        assert result == {
            "error": "Invalid input",
            "details": "Tool input must be a dictionary",
        }


def test_tool_results_are_deterministic_for_identical_input() -> None:
    verify_payload = {"argument": "P -> Q, P |- Q"}
    assumptions_payload = {
        "assumptions": [
            {"id": "a1", "statement": "x > 0", "kind": "assumption"},
            {"id": "a2", "statement": "x < 10", "kind": "fact"},
        ],
        "variables": {"x": "Int"},
    }
    counterfactual_payload = {
        "variables": {"x": "Int"},
        "base_constraints": ["x > 0"],
        "branches": {"b1": ["x < 10"]},
    }
    z3_payload = {
        "variables": {"x": "Int"},
        "constraints": ["x > 0", "x < 10"],
    }
    policy_payload = {
        "rules": [
            {
                "name": "dependency_review",
                "severity": "warning",
                "message": "New dependencies require review",
                "when_true": ["adds_dependency"],
            }
        ],
        "action": {"adds_dependency": True},
    }

    assert verify_argument(verify_payload) == verify_argument(verify_payload)
    assert check_assumptions(assumptions_payload) == check_assumptions(assumptions_payload)
    assert counterfactual_branch(counterfactual_payload) == counterfactual_branch(counterfactual_payload)
    assert z3_check(z3_payload) == z3_check(z3_payload)
    assert check_policy(policy_payload) == check_policy(policy_payload)
