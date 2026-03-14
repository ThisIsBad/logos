"""Confidence calibration and escalation policy for reasoning outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from logic_brain.certificate import ProofCertificate

SCHEMA_VERSION = "1.0"


class ConfidenceLevel(Enum):
    """Calibrated confidence levels."""

    CERTAIN = "certain"
    SUPPORTED = "supported"
    WEAK = "weak"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Action risk levels used by escalation checks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EscalationDecision(Enum):
    """Escalation outcomes for a confidence/risk pair."""

    PROCEED = "proceed"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ConfidenceRecord:
    """Confidence state with provenance metadata."""

    claim: str
    level: ConfidenceLevel
    provenance: tuple[str, ...]
    linked_certificate: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialize confidence record to dictionary."""
        return {
            "schema_version": SCHEMA_VERSION,
            "claim": self.claim,
            "level": self.level.value,
            "provenance": list(self.provenance),
            "linked_certificate": self.linked_certificate,
        }

    def to_json(self) -> str:
        """Serialize confidence record to JSON."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ConfidenceRecord":
        """Deserialize confidence record from dictionary."""
        schema_version = payload.get("schema_version")
        claim = payload.get("claim")
        level = payload.get("level")
        provenance = payload.get("provenance")
        linked_certificate = payload.get("linked_certificate")

        if schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported uncertainty schema version '{schema_version}'")
        if not isinstance(claim, str):
            raise ValueError("Confidence payload field 'claim' must be a string")
        if not isinstance(level, str):
            raise ValueError("Confidence payload field 'level' must be a string")
        if not isinstance(provenance, list) or not all(isinstance(v, str) for v in provenance):
            raise ValueError("Confidence payload field 'provenance' must be list[str]")
        if linked_certificate is not None and not isinstance(linked_certificate, str):
            raise ValueError("Confidence payload field 'linked_certificate' must be str or null")

        return cls(
            claim=claim,
            level=ConfidenceLevel(level),
            provenance=tuple(provenance),
            linked_certificate=linked_certificate,
        )

    @classmethod
    def from_json(cls, raw_json: str) -> "ConfidenceRecord":
        """Deserialize confidence record from JSON."""
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid confidence JSON") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Confidence JSON must be an object")

        normalized = {str(key): value for key, value in parsed.items()}
        return cls.from_dict(normalized)


@dataclass(frozen=True)
class EscalationResult:
    """Result of applying uncertainty escalation policy."""

    decision: EscalationDecision
    reason: str


@dataclass(frozen=True)
class UncertaintyPolicy:
    """Escalation policy by risk level and confidence state."""

    high_risk_block: tuple[ConfidenceLevel, ...] = (ConfidenceLevel.WEAK, ConfidenceLevel.UNKNOWN)
    medium_risk_review: tuple[ConfidenceLevel, ...] = (ConfidenceLevel.WEAK, ConfidenceLevel.UNKNOWN)


class UncertaintyCalibrator:
    """Deterministically calibrate confidence and enforce escalation."""

    def classify(
        self,
        verified: bool,
        evidence_count: int = 1,
        conflicting_signals: bool = False,
    ) -> ConfidenceLevel:
        """Classify confidence from verification signals."""
        if conflicting_signals:
            return ConfidenceLevel.UNKNOWN
        if verified and evidence_count >= 2:
            return ConfidenceLevel.CERTAIN
        if verified:
            return ConfidenceLevel.SUPPORTED
        return ConfidenceLevel.WEAK

    def from_certificate(
        self,
        certificate: ProofCertificate,
        provenance: list[str] | None = None,
        conflicting_signals: bool = False,
    ) -> ConfidenceRecord:
        """Build confidence record from proof certificate output."""
        level = self.classify(
            verified=certificate.verified,
            evidence_count=len(provenance or [certificate.method]),
            conflicting_signals=conflicting_signals,
        )
        return ConfidenceRecord(
            claim=str(certificate.claim),
            level=level,
            provenance=tuple(provenance or [certificate.method]),
            linked_certificate=certificate.to_json(),
        )

    def enforce(
        self,
        record: ConfidenceRecord,
        risk_level: RiskLevel,
        policy: UncertaintyPolicy | None = None,
    ) -> EscalationResult:
        """Apply escalation policy for a confidence record."""
        active_policy = policy or UncertaintyPolicy()

        if risk_level is RiskLevel.HIGH and record.level in active_policy.high_risk_block:
            return EscalationResult(
                decision=EscalationDecision.BLOCKED,
                reason="High-risk action blocked due to weak or unknown confidence",
            )

        if risk_level is RiskLevel.MEDIUM and record.level in active_policy.medium_risk_review:
            return EscalationResult(
                decision=EscalationDecision.REVIEW_REQUIRED,
                reason="Medium-risk action requires review for weak or unknown confidence",
            )

        if risk_level is RiskLevel.HIGH and record.level is ConfidenceLevel.SUPPORTED:
            return EscalationResult(
                decision=EscalationDecision.REVIEW_REQUIRED,
                reason="High-risk action requires review unless confidence is certain",
            )

        return EscalationResult(
            decision=EscalationDecision.PROCEED,
            reason="Confidence is sufficient for selected risk level",
        )

    def is_policy_compliant(
        self,
        record: ConfidenceRecord,
        risk_level: RiskLevel,
        decision: EscalationDecision,
        policy: UncertaintyPolicy | None = None,
    ) -> bool:
        """Check whether an external decision follows escalation policy."""
        expected = self.enforce(record=record, risk_level=risk_level, policy=policy)
        return decision is expected.decision
