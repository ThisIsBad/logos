"""Metamorphic tests for certificate store proof memory."""

from __future__ import annotations

import pytest

from logic_brain import CertificateStore, certify


pytestmark = pytest.mark.metamorphic


def test_store_query_idempotence() -> None:
    """Storing the same certificate twice does not change query results."""
    store = CertificateStore()
    cert = certify("P -> Q, P |- Q")

    store.store(cert, tags={"domain": "budget"})
    first = store.query()
    store.store(cert, tags={"step": "1"})
    second = store.query()

    assert len(first) == len(second) == 1
    assert first[0].store_id == second[0].store_id
    assert second[0].tags == {"domain": "budget", "step": "1"}


def test_prune_monotonicity() -> None:
    """Pruning never increases the number of entries."""
    store = CertificateStore()
    first_id = store.store(certify("P -> Q, P |- Q"))
    store.store(certify("P -> Q, Q |- P"))
    store.invalidate(first_id, reason="test")

    before = store.stats().total
    store.prune(invalidated_only=True)
    after = store.stats().total

    assert after <= before


def test_invalidation_irreversibility() -> None:
    """Once invalidated, calling invalidate again is a no-op."""
    store = CertificateStore()
    cert = certify("P -> Q, P |- Q")
    store_id = store.store(cert)

    first = store.invalidate(store_id, reason="test")
    second = store.invalidate(store_id, reason="different reason")

    assert first.invalidated_at == second.invalidated_at
    assert first.invalidation_reason == second.invalidation_reason
