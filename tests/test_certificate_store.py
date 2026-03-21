"""Tests for certificate store proof memory."""

from __future__ import annotations

from logic_brain import CertificateStore, ProofCertificate, StoreStats, StoredCertificate, certify


def _valid_cert() -> ProofCertificate:
    return certify("P -> Q, P |- Q")


def _invalid_cert() -> ProofCertificate:
    return certify("P -> Q, Q |- P")


def _dict_claim_cert() -> ProofCertificate:
    return ProofCertificate(
        claim={"goal": "budget", "value": "<= 100"},
        method="z3_session",
        verified=True,
        timestamp="2026-03-21T00:00:00+00:00",
        verification_artifact={"status": "sat"},
        claim_type="z3_session",
    )


def _store_from_entries(*entries: StoredCertificate) -> CertificateStore:
    return CertificateStore.from_dict(
        {
            "schema_version": "1.0",
            "entries": [entry.to_dict() for entry in entries],
        }
    )


def test_store_is_idempotent_and_merges_tags() -> None:
    store = CertificateStore()
    cert = _valid_cert()

    first_id = store.store(cert, tags={"domain": "budget"})
    second_id = store.store(cert, tags={"step": "1"})

    assert first_id == second_id
    stored = store.get(first_id)
    assert stored is not None
    assert stored.tags == {"domain": "budget", "step": "1"}
    assert store.stats().total == 1


def test_get_returns_none_for_unknown_store_id() -> None:
    assert CertificateStore().get("missing") is None


def test_query_filters_by_method_verified_tags_and_invalidated_state() -> None:
    valid = StoredCertificate(
        store_id="a",
        certificate=_valid_cert(),
        tags={"domain": "budget", "env": "prod"},
        stored_at="2026-03-21T01:00:00+00:00",
    )
    invalid = StoredCertificate(
        store_id="b",
        certificate=_invalid_cert(),
        tags={"domain": "budget", "env": "dev"},
        stored_at="2026-03-21T02:00:00+00:00",
        invalidated_at="2026-03-21T03:00:00+00:00",
        invalidation_reason="superseded",
    )
    store = _store_from_entries(valid, invalid)

    assert [entry.store_id for entry in store.query(method="z3_propositional", verified=True)] == ["a"]
    assert [entry.store_id for entry in store.query(tags={"domain": "budget", "env": "prod"})] == ["a"]
    assert [entry.store_id for entry in store.query(include_invalidated=True, verified=False)] == ["b"]


def test_query_filters_by_claim_pattern_since_and_descending_order() -> None:
    older = StoredCertificate(
        store_id="older",
        certificate=_valid_cert(),
        tags={"domain": "logic"},
        stored_at="2026-03-21T01:00:00+00:00",
    )
    newer = StoredCertificate(
        store_id="newer",
        certificate=_dict_claim_cert(),
        tags={"domain": "budget"},
        stored_at="2026-03-21T02:00:00+00:00",
    )
    store = _store_from_entries(older, newer)

    assert [entry.store_id for entry in store.query(claim_pattern="budget", include_invalidated=True)] == ["newer"]
    assert [
        entry.store_id
        for entry in store.query(since="2026-03-21T01:30:00+00:00", include_invalidated=True)
    ] == ["newer"]
    assert [entry.store_id for entry in store.query(include_invalidated=True)] == ["newer", "older"]


def test_query_limit_zero_and_negative_limit_handling() -> None:
    store = CertificateStore()
    store.store(_valid_cert())

    assert store.query(limit=0) == []

    try:
        store.query(limit=-1)
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError for negative limit")


def test_invalidate_is_irreversible_and_requires_existing_entry() -> None:
    store = CertificateStore()
    cert = _valid_cert()
    store_id = store.store(cert)

    first = store.invalidate(store_id, reason="retracted")
    second = store.invalidate(store_id, reason="ignored")

    assert first.invalidated_at is not None
    assert second.invalidated_at == first.invalidated_at
    assert second.invalidation_reason == "retracted"

    try:
        store.invalidate("missing", reason="x")
    except ValueError as exc:
        assert "Unknown certificate store id" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError for missing store id")


def test_prune_removes_entries_and_supports_and_semantics() -> None:
    old_valid = StoredCertificate(
        store_id="old-valid",
        certificate=_valid_cert(),
        tags={},
        stored_at="2000-01-01T00:00:00+00:00",
    )
    old_invalid = StoredCertificate(
        store_id="old-invalid",
        certificate=_invalid_cert(),
        tags={},
        stored_at="2000-01-01T00:00:00+00:00",
        invalidated_at="2000-01-02T00:00:00+00:00",
        invalidation_reason="old",
    )
    recent_invalid = StoredCertificate(
        store_id="recent-invalid",
        certificate=_invalid_cert(),
        tags={},
        stored_at="2999-01-01T00:00:00+00:00",
        invalidated_at="2999-01-02T00:00:00+00:00",
        invalidation_reason="future",
    )
    store = _store_from_entries(old_valid, old_invalid, recent_invalid)

    assert store.prune(max_age_seconds=1.0, invalidated_only=True) == 1
    assert store.get("old-invalid") is None
    assert store.get("old-valid") is not None
    assert store.get("recent-invalid") is not None

    assert store.prune(invalidated_only=True) == 1
    assert store.get("recent-invalid") is None


def test_stats_counts_total_valid_invalidated_and_breakdowns() -> None:
    store = _store_from_entries(
        StoredCertificate("a", _valid_cert(), {}, "2026-03-21T01:00:00+00:00"),
        StoredCertificate(
            "b",
            _dict_claim_cert(),
            {},
            "2026-03-21T02:00:00+00:00",
            invalidated_at="2026-03-21T03:00:00+00:00",
            invalidation_reason="superseded",
        ),
    )

    stats = store.stats()

    assert stats.total == 2
    assert stats.valid == 1
    assert stats.invalidated == 1
    assert stats.by_claim_type == {"propositional": 1, "z3_session": 1}
    assert stats.by_method == {"z3_propositional": 1, "z3_session": 1}


def test_serialization_round_trip_for_stored_certificate_stats_and_store() -> None:
    cert = _valid_cert()
    entry = StoredCertificate(
        store_id="entry-1",
        certificate=cert,
        tags={"domain": "budget"},
        stored_at="2026-03-21T01:00:00+00:00",
    )
    restored_entry = StoredCertificate.from_dict(entry.to_dict())
    assert restored_entry == entry

    stats = StoreStats(
        total=1,
        valid=1,
        invalidated=0,
        by_claim_type={"propositional": 1},
        by_method={"z3_propositional": 1},
    )
    restored_stats = StoreStats.from_dict(stats.to_dict())
    assert restored_stats == stats

    store = CertificateStore()
    store.store(cert, tags={"domain": "budget"})
    restored_store = CertificateStore.from_json(store.to_json())
    assert restored_store.to_dict() == store.to_dict()


def test_clear_empties_store() -> None:
    store = CertificateStore()
    store.store(_valid_cert())
    store.clear()
    assert store.stats().total == 0


def test_invalid_inputs_raise_descriptive_errors() -> None:
    try:
        StoredCertificate.from_dict({})
    except ValueError as exc:
        assert "store_id" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected StoredCertificate.from_dict to fail")

    try:
        StoreStats.from_dict({"total": 1, "valid": 1, "invalidated": 0, "by_claim_type": {"a": "x"}, "by_method": {}})
    except ValueError as exc:
        assert "integers" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected StoreStats.from_dict to fail")

    try:
        CertificateStore.from_dict({"schema_version": "2.0", "entries": []})
    except ValueError as exc:
        assert "Unsupported certificate store schema version" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected CertificateStore.from_dict to fail")

    try:
        CertificateStore().store(_valid_cert(), tags={"domain": 1})  # type: ignore[dict-item]
    except ValueError as exc:
        assert "dict[str, str]" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected invalid tags to fail")
