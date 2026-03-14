"""Causal and temporal belief graph for long-horizon reasoning."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from logic_brain.uncertainty import ConfidenceLevel, UncertaintyCalibrator


class BeliefEdgeType(Enum):
    """Typed causal edge labels for belief relations."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    OBSERVED_AT = "observed_at"


@dataclass(frozen=True)
class BeliefNode:
    """One belief node with temporal validity metadata."""

    belief_id: str
    statement: str
    valid_from: datetime
    valid_until: datetime | None = None
    ttl_seconds: int | None = None


@dataclass(frozen=True)
class BeliefEdge:
    """Directed relation between two belief nodes."""

    source_id: str
    target_id: str
    edge_type: BeliefEdgeType


@dataclass(frozen=True)
class ContradictionExplanation:
    """Explicit contradiction explanation as two support paths."""

    left_id: str
    right_id: str
    left_support_path: tuple[str, ...]
    right_support_path: tuple[str, ...]


class BeliefGraph:
    """Track causal provenance and temporal validity for beliefs."""

    def __init__(self) -> None:
        self._nodes: dict[str, BeliefNode] = {}
        self._edges: list[BeliefEdge] = []
        self._confidence: dict[str, ConfidenceLevel] = {}

    def add_belief(
        self,
        belief_id: str,
        statement: str,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
        ttl_seconds: int | None = None,
    ) -> BeliefNode:
        """Add a belief node with temporal metadata."""
        if belief_id in self._nodes:
            raise ValueError(f"Belief '{belief_id}' already exists")
        if not belief_id:
            raise ValueError("Belief id cannot be empty")
        if not statement:
            raise ValueError("Belief statement cannot be empty")
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("Belief ttl_seconds must be > 0")

        node = BeliefNode(
            belief_id=belief_id,
            statement=statement,
            valid_from=valid_from or datetime.now(timezone.utc),
            valid_until=valid_until,
            ttl_seconds=ttl_seconds,
        )
        self._nodes[belief_id] = node
        return node

    def add_edge(self, source_id: str, target_id: str, edge_type: BeliefEdgeType) -> BeliefEdge:
        """Add a typed edge between existing beliefs."""
        if source_id not in self._nodes:
            raise ValueError(f"Unknown belief id '{source_id}'")
        if target_id not in self._nodes:
            raise ValueError(f"Unknown belief id '{target_id}'")

        edge = BeliefEdge(source_id=source_id, target_id=target_id, edge_type=edge_type)
        if edge not in self._edges:
            self._edges.append(edge)
        return edge

    def get_belief(self, belief_id: str) -> BeliefNode:
        """Get belief node by id."""
        if belief_id not in self._nodes:
            raise ValueError(f"Unknown belief id '{belief_id}'")
        return self._nodes[belief_id]

    def beliefs(self) -> tuple[BeliefNode, ...]:
        """Return all beliefs sorted by id for deterministic iteration."""
        return tuple(self._nodes[key] for key in sorted(self._nodes))

    def edges(self) -> tuple[BeliefEdge, ...]:
        """Return all edges sorted deterministically."""
        return tuple(
            sorted(
                self._edges,
                key=lambda edge: (edge.edge_type.value, edge.source_id, edge.target_id),
            )
        )

    def minimal_support_set(self, belief_id: str) -> tuple[str, ...]:
        """Return minimal supporting root beliefs for a target belief."""
        self.get_belief(belief_id)
        support_types = {BeliefEdgeType.SUPPORTS, BeliefEdgeType.DERIVED_FROM}
        roots: set[str] = set()
        queue: deque[str] = deque([belief_id])
        seen: set[str] = set()

        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)

            parents = [
                edge.source_id
                for edge in self._edges
                if edge.target_id == current and edge.edge_type in support_types
            ]
            if not parents:
                roots.add(current)
                continue
            for parent in parents:
                queue.append(parent)

        return tuple(sorted(roots))

    def stale_dependencies(self, at_time: datetime | None = None) -> tuple[str, ...]:
        """Return stale dependencies that still support/derive other beliefs."""
        now = at_time or datetime.now(timezone.utc)
        support_types = {BeliefEdgeType.SUPPORTS, BeliefEdgeType.DERIVED_FROM}
        candidates = {
            edge.source_id
            for edge in self._edges
            if edge.edge_type in support_types
        }

        stale = [belief_id for belief_id in candidates if self._is_stale(self._nodes[belief_id], now)]
        return tuple(sorted(stale))

    def contradiction_frontier(self) -> tuple[tuple[str, str], ...]:
        """Return explicit contradictory belief pairs."""
        pairs: set[tuple[str, str]] = set()
        for edge in self._edges:
            if edge.edge_type is not BeliefEdgeType.CONTRADICTS:
                continue
            pair_values = sorted((edge.source_id, edge.target_id))
            left, right = pair_values[0], pair_values[1]
            pairs.add((left, right))
        return tuple(sorted(pairs))

    def explain_contradiction(self, left_id: str, right_id: str) -> ContradictionExplanation:
        """Explain contradiction with explicit support paths for both beliefs."""
        pair_values = sorted((left_id, right_id))
        pair = (pair_values[0], pair_values[1])
        if pair not in self.contradiction_frontier():
            raise ValueError(f"Beliefs '{left_id}' and '{right_id}' are not contradictory")

        return ContradictionExplanation(
            left_id=left_id,
            right_id=right_id,
            left_support_path=self._support_path_to_root(left_id),
            right_support_path=self._support_path_to_root(right_id),
        )

    def ingest_assumptions(self, assumptions: object) -> tuple[str, ...]:
        """Integration hook: ingest active assumptions as beliefs.

        The method accepts ``AssumptionSet`` to avoid hard coupling in typing.
        """
        active_entries = getattr(assumptions, "active_entries")
        if not callable(active_entries):
            raise ValueError("assumptions object must provide active_entries()")

        entries_obj = active_entries()
        if not isinstance(entries_obj, Iterable):
            raise ValueError("assumptions active_entries() must return an iterable")

        ingested: list[str] = []
        entries = entries_obj
        for entry in entries:
            belief_id = str(getattr(entry, "assumption_id"))
            statement = str(getattr(entry, "statement"))
            if belief_id not in self._nodes:
                self.add_belief(belief_id=belief_id, statement=statement)
            ingested.append(belief_id)
        return tuple(sorted(ingested))

    def calibrate_confidence(
        self,
        belief_id: str,
        calibrator: UncertaintyCalibrator,
        verified: bool,
        evidence_count: int = 1,
        conflicting_signals: bool = False,
    ) -> ConfidenceLevel:
        """Integration hook: attach calibrated confidence to one belief."""
        self.get_belief(belief_id)
        level = calibrator.classify(
            verified=verified,
            evidence_count=evidence_count,
            conflicting_signals=conflicting_signals,
        )
        self._confidence[belief_id] = level
        return level

    def confidence(self, belief_id: str) -> ConfidenceLevel | None:
        """Get stored confidence level for a belief."""
        self.get_belief(belief_id)
        return self._confidence.get(belief_id)

    def _is_stale(self, node: BeliefNode, at_time: datetime) -> bool:
        valid_until = self._effective_valid_until(node)
        if valid_until is None:
            return False
        return at_time > valid_until

    def _effective_valid_until(self, node: BeliefNode) -> datetime | None:
        if node.valid_until is not None:
            return node.valid_until
        if node.ttl_seconds is not None:
            return node.valid_from + timedelta(seconds=node.ttl_seconds)
        return None

    def _support_path_to_root(self, belief_id: str) -> tuple[str, ...]:
        support_types = {BeliefEdgeType.SUPPORTS, BeliefEdgeType.DERIVED_FROM}
        path: list[str] = [belief_id]
        current = belief_id

        while True:
            parents = sorted(
                [
                    edge.source_id
                    for edge in self._edges
                    if edge.target_id == current and edge.edge_type in support_types
                ]
            )
            if not parents:
                break
            current = parents[0]
            path.append(current)

        return tuple(path)
