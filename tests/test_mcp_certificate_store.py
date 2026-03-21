"""Tests for the certificate_store MCP handler."""

from __future__ import annotations

import logic_brain.mcp_tools as mcp_tools
from logic_brain import ProofCertificate, certify
from logic_brain.mcp_tools import certificate_store


def setup_function() -> None:
    mcp_tools._CERTIFICATE_STORE.clear()


def test_certificate_store_store_accepts_certificate_dict_and_reports_duplicate() -> None:
    cert = certify("P -> Q, P |- Q")

    first = certificate_store({"action": "store", "certificate": cert.to_dict(), "tags": {"domain": "budget"}})
    second = certificate_store({"action": "store", "certificate": cert.to_dict()})

    assert isinstance(first["store_id"], str)
    assert first["duplicate"] is False
    assert second["duplicate"] is True


def test_certificate_store_store_accepts_certificate_json() -> None:
    cert = certify("P -> Q, P |- Q")

    result = certificate_store({"action": "store", "certificate_json": cert.to_json()})

    assert isinstance(result["store_id"], str)
    assert result["duplicate"] is False
    assert isinstance(result["stored_at"], str)


def test_certificate_store_get_returns_found_false_when_missing() -> None:
    assert certificate_store({"action": "get", "store_id": "missing"}) == {"found": False}


def test_certificate_store_get_returns_serialized_entry() -> None:
    cert = certify("P -> Q, P |- Q")
    stored = certificate_store({"action": "store", "certificate": cert.to_dict(), "tags": {"domain": "budget"}})

    result = certificate_store({"action": "get", "store_id": stored["store_id"]})

    assert result["found"] is True
    entry = result["entry"]
    assert isinstance(entry, dict)
    assert entry["tags"] == {"domain": "budget"}


def test_certificate_store_query_returns_count_and_entries() -> None:
    valid = certify("P -> Q, P |- Q")
    invalid = certify("P -> Q, Q |- P")
    first = certificate_store({"action": "store", "certificate": valid.to_dict(), "tags": {"domain": "budget"}})
    second = certificate_store({"action": "store", "certificate": invalid.to_dict(), "tags": {"domain": "logic"}})
    certificate_store({"action": "invalidate", "store_id": second["store_id"], "reason": "retracted"})

    result = certificate_store(
        {
            "action": "query",
            "verified": True,
            "tags": {"domain": "budget"},
            "include_invalidated": False,
            "limit": 10,
        }
    )

    assert result["count"] == 1
    entries = result["entries"]
    assert isinstance(entries, list)
    assert entries[0]["store_id"] == first["store_id"]


def test_certificate_store_invalidate_returns_updated_entry() -> None:
    cert = certify("P -> Q, P |- Q")
    stored = certificate_store({"action": "store", "certificate": cert.to_dict()})

    result = certificate_store(
        {
            "action": "invalidate",
            "store_id": stored["store_id"],
            "reason": "Assumption budget <= 100 was retracted",
        }
    )

    assert result["store_id"] == stored["store_id"]
    assert isinstance(result["invalidated_at"], str)
    assert result["invalidation_reason"] == "Assumption budget <= 100 was retracted"


def test_certificate_store_stats_returns_aggregate_counts() -> None:
    certificate_store({"action": "store", "certificate": certify("P -> Q, P |- Q").to_dict()})
    invalid = certificate_store({"action": "store", "certificate": certify("P -> Q, Q |- P").to_dict()})
    certificate_store({"action": "invalidate", "store_id": invalid["store_id"], "reason": "obsolete"})

    result = certificate_store({"action": "stats"})

    assert result["total"] == 2
    assert result["valid"] == 1
    assert result["invalidated"] == 1


def test_certificate_store_rejects_missing_or_conflicting_store_inputs() -> None:
    missing = certificate_store({"action": "store"})
    both = certificate_store(
        {
            "action": "store",
            "certificate": certify("P -> Q, P |- Q").to_dict(),
            "certificate_json": certify("P -> Q, P |- Q").to_json(),
        }
    )

    assert missing["error"] == "Invalid input"
    assert both["error"] == "Invalid input"


def test_certificate_store_rejects_missing_required_fields_and_invalid_certificate_payload() -> None:
    missing_get = certificate_store({"action": "get"})
    missing_invalidate = certificate_store({"action": "invalidate", "store_id": "abc"})
    invalid_cert = certificate_store({"action": "store", "certificate": {"claim": "bad"}})

    assert missing_get["error"] == "Invalid input"
    assert missing_invalidate["error"] == "Invalid input"
    assert invalid_cert["error"] == "Invalid input"


def test_certificate_store_rejects_unknown_action() -> None:
    result = certificate_store({"action": "prune"})

    assert result["error"] == "Invalid input"


def test_certificate_store_can_round_trip_entry_certificate() -> None:
    cert = certify("P -> Q, P |- Q")
    stored = certificate_store({"action": "store", "certificate_json": cert.to_json()})
    entry_result = certificate_store({"action": "get", "store_id": stored["store_id"]})

    entry = entry_result["entry"]
    assert isinstance(entry, dict)
    certificate_data = entry["certificate"]
    assert isinstance(certificate_data, dict)
    restored = ProofCertificate.from_dict(certificate_data)
    assert restored == cert
