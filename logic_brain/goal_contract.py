"""Goal contracts and deterministic strategy verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from logic_brain.action_policy import ActionPolicyEngine, PolicyDecision
from logic_brain.counterfactual import PlanBranch
from logic_brain.schema_utils import (
    load_json_object,
    require_list_of_str,
    require_str,
)

SCHEMA_VERSION = "1.0"


class GoalContractStatus(Enum):
    """Evaluation status for one goal contract check."""

    BLOCKED = "blocked"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"


@dataclass(frozen=True)
class GoalContractDiagnostic:
    """Structured diagnostics for contract violations or drift."""

    code: str
    message: str


@dataclass(frozen=True)
class GoalContract:
    """Machine-checkable goal contract."""

    contract_id: str
    preconditions: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()
    completion_criteria: tuple[str, ...] = ()
    abort_criteria: tuple[str, ...] = ()
    permitted_strategies: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize contract payload."""
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "preconditions": list(self.preconditions),
            "invariants": list(self.invariants),
            "completion_criteria": list(self.completion_criteria),
            "abort_criteria": list(self.abort_criteria),
            "permitted_strategies": list(self.permitted_strategies),
        }

    def to_json(self) -> str:
        """Serialize contract to JSON."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "GoalContract":
        """Deserialize contract from dictionary."""
        schema_version = require_str(
            payload.get("schema_version"),
            "Goal contract field 'schema_version' must be a string",
        )
        if schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported goal contract schema version '{schema_version}'")

        contract_id = require_str(
            payload.get("contract_id"),
            "Goal contract field 'contract_id' must be a string",
        )
        preconditions = tuple(
            require_list_of_str(
                payload.get("preconditions", []),
                "Goal contract field 'preconditions' must be list[str]",
            )
        )
        invariants = tuple(
            require_list_of_str(
                payload.get("invariants", []),
                "Goal contract field 'invariants' must be list[str]",
            )
        )
        completion_criteria = tuple(
            require_list_of_str(
                payload.get("completion_criteria", []),
                "Goal contract field 'completion_criteria' must be list[str]",
            )
        )
        abort_criteria = tuple(
            require_list_of_str(
                payload.get("abort_criteria", []),
                "Goal contract field 'abort_criteria' must be list[str]",
            )
        )
        permitted_strategies = tuple(
            require_list_of_str(
                payload.get("permitted_strategies", []),
                "Goal contract field 'permitted_strategies' must be list[str]",
            )
        )

        return cls(
            contract_id=contract_id,
            preconditions=preconditions,
            invariants=invariants,
            completion_criteria=completion_criteria,
            abort_criteria=abort_criteria,
            permitted_strategies=permitted_strategies,
            schema_version=schema_version,
        )

    @classmethod
    def from_json(cls, raw_json: str) -> "GoalContract":
        """Deserialize contract from JSON."""
        payload = load_json_object(
            raw_json,
            invalid_error="Invalid goal contract JSON",
            object_error="Goal contract JSON must be an object",
        )
        return cls.from_dict(payload)


@dataclass(frozen=True)
class GoalContractResult:
    """Deterministic evaluation output for one contract check."""

    status: GoalContractStatus
    diagnostics: tuple[GoalContractDiagnostic, ...]
    policy_decision: PolicyDecision | None = None


def build_branch_context(branch: PlanBranch) -> dict[str, bool]:
    """Build a deterministic boolean context from a planner branch."""
    return {
        "sat": branch.satisfiable is True,
        "unsat": branch.satisfiable is False,
        "unknown": branch.satisfiable is None,
        "has_scores": len(branch.scores) > 0,
    }


def evaluate_goal_contract(
    contract: GoalContract,
    *,
    strategy: str,
    context: dict[str, bool],
    policy_engine: ActionPolicyEngine | None = None,
    policy_action: dict[str, bool] | None = None,
) -> GoalContractResult:
    """Evaluate a goal contract deterministically against a context."""
    diagnostics: list[GoalContractDiagnostic] = []
    policy_decision: PolicyDecision | None = None

    if contract.permitted_strategies and strategy not in contract.permitted_strategies:
        diagnostics.append(
            GoalContractDiagnostic(
                code="strategy_not_permitted",
                message=f"Strategy '{strategy}' is not permitted by contract",
            )
        )
        return GoalContractResult(status=GoalContractStatus.BLOCKED, diagnostics=tuple(diagnostics))

    if not _all_clauses_hold(contract.preconditions, context):
        diagnostics.append(
            GoalContractDiagnostic(
                code="precondition_failed",
                message="One or more preconditions are not satisfied",
            )
        )
        return GoalContractResult(status=GoalContractStatus.BLOCKED, diagnostics=tuple(diagnostics))

    if _any_clause_holds(contract.abort_criteria, context):
        diagnostics.append(
            GoalContractDiagnostic(
                code="abort_criteria_triggered",
                message="Abort criteria triggered",
            )
        )
        return GoalContractResult(status=GoalContractStatus.ABORTED, diagnostics=tuple(diagnostics))

    if not _all_clauses_hold(contract.invariants, context):
        diagnostics.append(
            GoalContractDiagnostic(
                code="invariant_failed",
                message="Invariant drift detected",
            )
        )
        return GoalContractResult(status=GoalContractStatus.ABORTED, diagnostics=tuple(diagnostics))

    if policy_engine is not None:
        action_context = policy_action or context
        policy_result = policy_engine.evaluate(action_context)
        policy_decision = policy_result.decision
        if policy_result.decision is PolicyDecision.BLOCK:
            diagnostics.append(
                GoalContractDiagnostic(
                    code="policy_block",
                    message="Action policy blocked the contract execution",
                )
            )
            return GoalContractResult(
                status=GoalContractStatus.BLOCKED,
                diagnostics=tuple(diagnostics),
                policy_decision=policy_decision,
            )

    if contract.completion_criteria and _all_clauses_hold(contract.completion_criteria, context):
        return GoalContractResult(
            status=GoalContractStatus.COMPLETED,
            diagnostics=tuple(diagnostics),
            policy_decision=policy_decision,
        )

    return GoalContractResult(
        status=GoalContractStatus.ACTIVE,
        diagnostics=tuple(diagnostics),
        policy_decision=policy_decision,
    )


def _all_clauses_hold(clauses: tuple[str, ...], context: dict[str, bool]) -> bool:
    return all(_evaluate_clause(clause, context) for clause in clauses)


def _any_clause_holds(clauses: tuple[str, ...], context: dict[str, bool]) -> bool:
    return any(_evaluate_clause(clause, context) for clause in clauses)


def _evaluate_clause(clause: str, context: dict[str, bool]) -> bool:
    if clause.startswith("!"):
        key = clause[1:]
        return not context.get(key, False)
    return context.get(clause, False)


def verify_contract_preconditions_z3(
    contract: GoalContract,
    state_constraints: list[str],
    variables: dict[str, str] | None = None,
    timeout_ms: int = 30000,
) -> GoalContractResult:
    """Verify goal contract preconditions against Z3 state constraints.

    Each precondition and state constraint is parsed as a Z3 formula.
    The check asks: given the state constraints, are all preconditions
    necessarily satisfied?

    This uses proof-by-refutation: assert state constraints and the
    negation of a precondition. If UNSAT, the precondition holds.

    Parameters
    ----------
    contract : GoalContract
        The contract whose preconditions to verify.
    state_constraints : list[str]
        Z3-parseable constraints describing the current state.
    variables : dict[str, str] | None
        Variable declarations as ``{name: sort}``.
    timeout_ms : int
        Z3 solver timeout.

    Returns
    -------
    GoalContractResult
        ACTIVE if all preconditions hold, BLOCKED if any fails.
    """
    from logic_brain.z3_session import Z3Session

    diagnostics: list[GoalContractDiagnostic] = []

    for precondition in contract.preconditions:
        session = Z3Session(timeout_ms=timeout_ms)

        if variables is not None:
            for var_name, sort in variables.items():
                session.declare(var_name, sort)
        else:
            _auto_declare_contract_variables(
                session, state_constraints + [precondition]
            )

        for constraint in state_constraints:
            session.assert_constraint(constraint)

        # Negate the precondition — if UNSAT, precondition must hold
        session.assert_constraint(f"not ({precondition})")

        result = session.check()
        if result.satisfiable is not False:
            # SAT or unknown means precondition is not guaranteed
            diagnostics.append(
                GoalContractDiagnostic(
                    code="z3_precondition_not_entailed",
                    message=f"Precondition '{precondition}' is not entailed by state",
                )
            )

    if diagnostics:
        return GoalContractResult(
            status=GoalContractStatus.BLOCKED,
            diagnostics=tuple(diagnostics),
        )

    return GoalContractResult(
        status=GoalContractStatus.ACTIVE,
        diagnostics=(),
    )


def _auto_declare_contract_variables(
    session: object, statements: list[str]
) -> None:
    """Best-effort auto-declare single-letter variables as Int."""
    import re

    declare = getattr(session, "declare")
    declared: set[str] = set()
    for statement in statements:
        for match in re.finditer(r"\b([a-z])\b", statement):
            name = match.group(1)
            if name not in declared:
                declare(name, "Int")
                declared.add(name)
