"""Metamorphic tests for proof certificates (Issue #30)."""

from __future__ import annotations

import pytest

from logic_brain import ProofCertificate, certify, verify_certificate
from logic_brain.z3_session import Z3Session


pytestmark = pytest.mark.metamorphic


def test_mr_certificate_json_roundtrip_preserves_verification_state_propositional() -> None:
    cert = certify("P -> Q, P |- Q")
    restored = ProofCertificate.from_json(cert.to_json())

    assert verify_certificate(cert) is verify_certificate(restored)
    assert restored.verified is cert.verified


def test_mr_certificate_json_roundtrip_preserves_verification_state_z3_session() -> None:
    session = Z3Session()
    session.declare("x", "Int")
    session.assert_constraint("x > 5")
    session.assert_constraint("x < 8")

    cert = certify(session)
    restored = ProofCertificate.from_json(cert.to_json())

    assert verify_certificate(cert) is verify_certificate(restored)
    assert restored.verified is cert.verified
