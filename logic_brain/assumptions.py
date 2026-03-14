"""Typed assumption state management for long-horizon reasoning."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from logic_brain.schema_utils import (
    load_json_object,
    require_dict,
    require_list,
    require_optional_str,
    require_str,
)

SCHEMA_VERSION = "1.0"


class AssumptionKind(Enum):
    """Typed assumption categories."""

    FACT = "fact"
    ASSUMPTION = "assumption"
    HYPOTHESIS = "hypothesis"


class AssumptionStatus(Enum):
    """Lifecycle states for assumptions."""

    ACTIVE = "active"
    EXPIRED = "expired"
    RETRACTED = "retracted"


@dataclass(frozen=True)
class AssumptionEntry:
    """Single assumption with provenance and lifecycle metadata."""

    assumption_id: str
    statement: str
    kind: AssumptionKind
    source: str
    timestamp: str
    scope: str | None = None
    expires_at: str | None = None
    status: AssumptionStatus = AssumptionStatus.ACTIVE


@dataclass(frozen=True)
class AssumptionConsistency:
    """Consistency result over active assumptions."""

    consistent: bool
    active_statements: list[str]


class AssumptionSet:
    """Manage typed assumptions with deterministic lifecycle operations."""

    def __init__(self, schema_version: str = SCHEMA_VERSION) -> None:
        if schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported assumption schema version '{schema_version}'")
        self.schema_version = schema_version
        self._entries: dict[str, AssumptionEntry] = {}

    def add(
        self,
        assumption_id: str,
        statement: str,
        kind: AssumptionKind,
        source: str,
        scope: str | None = None,
        expires_at: str | None = None,
        timestamp: str | None = None,
    ) -> AssumptionEntry:
        """Add a new active assumption entry."""
        if assumption_id in self._entries:
            raise ValueError(f"Assumption '{assumption_id}' already exists")

        if not assumption_id:
            raise ValueError("Assumption id cannot be empty")
        if not statement:
            raise ValueError("Assumption statement cannot be empty")
        if not source:
            raise ValueError("Assumption source cannot be empty")

        entry = AssumptionEntry(
            assumption_id=assumption_id,
            statement=statement,
            kind=kind,
            source=source,
            timestamp=timestamp or _utc_now_iso(),
            scope=scope,
            expires_at=expires_at,
            status=AssumptionStatus.ACTIVE,
        )
        self._entries[assumption_id] = entry
        return entry

    def activate(self, assumption_id: str) -> AssumptionEntry:
        """Activate an expired assumption."""
        return self._transition(assumption_id, AssumptionStatus.ACTIVE)

    def expire(self, assumption_id: str) -> AssumptionEntry:
        """Expire an active assumption."""
        return self._transition(assumption_id, AssumptionStatus.EXPIRED)

    def retract(self, assumption_id: str) -> AssumptionEntry:
        """Retract an assumption (idempotent)."""
        entry = self._get_required(assumption_id)
        if entry.status is AssumptionStatus.RETRACTED:
            return entry

        updated = replace(entry, status=AssumptionStatus.RETRACTED)
        self._entries[assumption_id] = updated
        return updated

    def get(self, assumption_id: str) -> AssumptionEntry | None:
        """Get an assumption by id."""
        return self._entries.get(assumption_id)

    def list_entries(self) -> list[AssumptionEntry]:
        """List all entries in insertion order."""
        return list(self._entries.values())

    def active_entries(self) -> list[AssumptionEntry]:
        """Return currently active assumptions."""
        return [entry for entry in self._entries.values() if entry.status is AssumptionStatus.ACTIVE]

    def active_statements(self) -> list[str]:
        """Return active assumption statements."""
        return [entry.statement for entry in self.active_entries()]

    def belief_payload(self) -> list[dict[str, str]]:
        """Export active assumptions as belief-style labeled assertions."""
        return [
            {"label": entry.assumption_id, "assertion": entry.statement}
            for entry in self.active_entries()
        ]

    def check_consistency(
        self,
        checker: Callable[[list[str]], bool],
    ) -> AssumptionConsistency:
        """Run an external consistency checker on active statements.

        This hook allows wiring to v0.5 BeliefSet when available.
        """
        statements = self.active_statements()
        return AssumptionConsistency(
            consistent=checker(statements),
            active_statements=statements,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "schema_version": self.schema_version,
            "assumptions": [
                {
                    "assumption_id": entry.assumption_id,
                    "statement": entry.statement,
                    "kind": entry.kind.value,
                    "source": entry.source,
                    "timestamp": entry.timestamp,
                    "scope": entry.scope,
                    "expires_at": entry.expires_at,
                    "status": entry.status.value,
                }
                for entry in self._entries.values()
            ],
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AssumptionSet":
        """Deserialize from dictionary payload."""
        schema_version = require_str(
            payload.get("schema_version"),
            "Assumption payload requires string field 'schema_version'",
        )
        assumptions = require_list(
            payload.get("assumptions"),
            "Assumption payload requires list field 'assumptions'",
        )

        instance = cls(schema_version=schema_version)

        for item in assumptions:
            item_dict = require_dict(item, "Assumption entries must be objects")

            assumption_id = require_str(
                item_dict.get("assumption_id"),
                "Assumption field 'assumption_id' must be a string",
            )
            statement = require_str(
                item_dict.get("statement"),
                "Assumption field 'statement' must be a string",
            )
            kind = require_str(
                item_dict.get("kind"),
                "Assumption field 'kind' must be a string",
            )
            source = require_str(
                item_dict.get("source"),
                "Assumption field 'source' must be a string",
            )
            timestamp = require_str(
                item_dict.get("timestamp"),
                "Assumption field 'timestamp' must be a string",
            )
            scope = require_optional_str(
                item_dict.get("scope"),
                "Assumption field 'scope' must be a string or null",
            )
            expires_at = require_optional_str(
                item_dict.get("expires_at"),
                "Assumption field 'expires_at' must be a string or null",
            )
            status = require_str(
                item_dict.get("status"),
                "Assumption field 'status' must be a string",
            )

            entry = AssumptionEntry(
                assumption_id=assumption_id,
                statement=statement,
                kind=AssumptionKind(kind),
                source=source,
                timestamp=timestamp,
                scope=scope,
                expires_at=expires_at,
                status=AssumptionStatus(status),
            )
            instance._entries[assumption_id] = entry

        return instance

    @classmethod
    def from_json(cls, raw_json: str) -> "AssumptionSet":
        """Deserialize from JSON string."""
        payload = load_json_object(
            raw_json,
            invalid_error="Invalid assumptions JSON",
            object_error="Assumptions JSON must be an object",
        )
        return cls.from_dict(payload)

    def _transition(self, assumption_id: str, target: AssumptionStatus) -> AssumptionEntry:
        entry = self._get_required(assumption_id)

        if entry.status is AssumptionStatus.RETRACTED:
            raise ValueError("Retracted assumptions cannot change lifecycle state")

        if target is AssumptionStatus.ACTIVE and entry.status is not AssumptionStatus.EXPIRED:
            raise ValueError("Only expired assumptions can be activated")

        if target is AssumptionStatus.EXPIRED and entry.status is not AssumptionStatus.ACTIVE:
            raise ValueError("Only active assumptions can be expired")

        updated = replace(entry, status=target)
        self._entries[assumption_id] = updated
        return updated

    def _get_required(self, assumption_id: str) -> AssumptionEntry:
        entry = self._entries.get(assumption_id)
        if entry is None:
            raise ValueError(f"Unknown assumption id '{assumption_id}'")
        return entry


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
