"""Counterfactual planning with deterministic branch replay."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Mapping

from logic_brain.certificate import ProofCertificate, certify, verify_certificate
from logic_brain.z3_session import Z3Session


@dataclass(frozen=True)
class VariableDecl:
    """Variable declaration in a planning state."""

    name: str
    sort: str
    size: int | None = None


@dataclass(frozen=True)
class PlanState:
    """Immutable state snapshot for one planning branch."""

    declarations: tuple[VariableDecl, ...] = ()
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanBranch:
    """One branch in a counterfactual plan tree."""

    branch_id: str
    parent_id: str | None
    state: PlanState
    status: str
    satisfiable: bool | None
    certificate: ProofCertificate
    trace: tuple[str, ...] = ()
    scores: Mapping[str, float] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class PlanResult:
    """Snapshot of planner branches."""

    branches: dict[str, PlanBranch]


class CounterfactualPlanner:
    """Deterministic counterfactual planner over Z3Session semantics."""

    def __init__(self, timeout_ms: int = 30000, track_unsat_core: bool = False) -> None:
        self.timeout_ms = timeout_ms
        self.track_unsat_core = track_unsat_core
        self._root_state = PlanState()
        self._branches: dict[str, PlanBranch] = {}

    def declare(self, name: str, sort: str, size: int | None = None) -> None:
        """Add a declaration to the root planning state."""
        if any(decl.name == name for decl in self._root_state.declarations):
            raise ValueError(f"Variable '{name}' already declared in root state")

        declarations = self._root_state.declarations + (VariableDecl(name, sort, size),)
        self._root_state = PlanState(declarations=declarations, constraints=self._root_state.constraints)

    def assert_constraint(self, constraint: str) -> None:
        """Add a root constraint for all future branches."""
        self._root_state = PlanState(
            declarations=self._root_state.declarations,
            constraints=self._root_state.constraints + (constraint,),
        )

    def branch(
        self,
        branch_id: str,
        additional_constraints: list[str] | None = None,
        parent_id: str | None = None,
    ) -> PlanBranch:
        """Create and evaluate a branch from root or an existing branch."""
        if branch_id in self._branches:
            raise ValueError(f"Branch '{branch_id}' already exists")

        parent_state, trace = self._resolve_parent_state(parent_id)
        extra_constraints = tuple(additional_constraints or [])
        new_state = PlanState(
            declarations=parent_state.declarations,
            constraints=parent_state.constraints + extra_constraints,
        )

        result = self._evaluate_state(new_state)
        new_trace = trace + tuple(f"assert {c}" for c in extra_constraints)
        branch = PlanBranch(
            branch_id=branch_id,
            parent_id=parent_id,
            state=new_state,
            status=result.status,
            satisfiable=result.satisfiable,
            certificate=result.certificate,
            trace=new_trace,
            scores=_frozen_scores(),
        )
        self._branches[branch_id] = branch
        return branch

    def replay(self, branch_id: str) -> PlanBranch:
        """Rebuild a branch from snapshot state and re-evaluate deterministically."""
        branch = self.get_branch(branch_id)
        replay_result = self._evaluate_state(branch.state)

        if replay_result.status != branch.status or replay_result.satisfiable != branch.satisfiable:
            raise ValueError("Branch replay diverged from recorded result")

        return PlanBranch(
            branch_id=branch.branch_id,
            parent_id=branch.parent_id,
            state=branch.state,
            status=replay_result.status,
            satisfiable=replay_result.satisfiable,
            certificate=replay_result.certificate,
            trace=branch.trace,
            scores=_frozen_scores(branch.scores),
        )

    def score_branch(self, branch_id: str, scorers: dict[str, Callable[[PlanBranch], float]]) -> PlanBranch:
        """Apply deterministic scoring hooks to a branch."""
        branch = self.get_branch(branch_id)
        new_scores = dict(branch.scores)
        for score_name, scorer in scorers.items():
            new_scores[score_name] = scorer(branch)

        updated = PlanBranch(
            branch_id=branch.branch_id,
            parent_id=branch.parent_id,
            state=branch.state,
            status=branch.status,
            satisfiable=branch.satisfiable,
            certificate=branch.certificate,
            trace=branch.trace,
            scores=_frozen_scores(new_scores),
        )
        self._branches[branch_id] = updated
        return updated

    def verify_branch_certificate(self, branch_id: str) -> bool:
        """Independent re-check for a branch certificate."""
        branch = self.get_branch(branch_id)
        return verify_certificate(branch.certificate)

    def get_branch(self, branch_id: str) -> PlanBranch:
        """Get an existing branch by id."""
        if branch_id not in self._branches:
            raise ValueError(f"Unknown branch '{branch_id}'")
        return self._branches[branch_id]

    def result(self) -> PlanResult:
        """Return snapshot of all created branches."""
        return PlanResult(branches=dict(self._branches))

    def _resolve_parent_state(self, parent_id: str | None) -> tuple[PlanState, tuple[str, ...]]:
        if parent_id is None:
            return self._root_state, ()

        if parent_id not in self._branches:
            raise ValueError(f"Unknown parent branch '{parent_id}'")

        parent = self._branches[parent_id]
        return parent.state, parent.trace + (f"fork {parent_id}",)

    def _evaluate_state(self, state: PlanState) -> PlanBranch:
        session = Z3Session(timeout_ms=self.timeout_ms, track_unsat_core=self.track_unsat_core)
        for decl in state.declarations:
            session.declare(decl.name, decl.sort, size=decl.size)
        for constraint in state.constraints:
            session.assert_constraint(constraint)

        check_result = session.check()
        certificate = certify(session)

        return PlanBranch(
            branch_id="__eval__",
            parent_id=None,
            state=state,
            status=check_result.status,
            satisfiable=check_result.satisfiable,
            certificate=certificate,
            scores=_frozen_scores(),
        )


def _frozen_scores(scores: Mapping[str, float] | None = None) -> Mapping[str, float]:
    return MappingProxyType(dict(scores or {}))
