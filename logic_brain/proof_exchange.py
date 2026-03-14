"""Transport-safe proof bundle exchange across process boundaries."""

from __future__ import annotations

import json
from dataclasses import dataclass

from logic_brain.certificate import ProofCertificate, verify_certificate

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ProofExchangeNode:
    """One certificate node and its dependency links."""

    node_id: str
    certificate: ProofCertificate
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProofBundle:
    """Versioned bundle for proof exchange."""

    schema_version: str
    nodes: dict[str, ProofExchangeNode]
    roots: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary payload."""
        return {
            "schema_version": self.schema_version,
            "roots": list(self.roots),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "certificate": node.certificate.to_dict(),
                    "depends_on": list(node.depends_on),
                }
                for node in self.nodes.values()
            ],
        }

    def to_json(self) -> str:
        """Serialize bundle to JSON."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ProofBundle":
        """Deserialize bundle from dictionary payload."""
        schema_version = payload.get("schema_version")
        roots = payload.get("roots")
        nodes = payload.get("nodes")

        if not isinstance(schema_version, str):
            raise ValueError("Proof bundle field 'schema_version' must be a string")
        if schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported proof bundle schema version '{schema_version}'")
        if not isinstance(roots, list) or not all(isinstance(v, str) for v in roots):
            raise ValueError("Proof bundle field 'roots' must be list[str]")
        if not isinstance(nodes, list):
            raise ValueError("Proof bundle field 'nodes' must be a list")

        parsed_nodes: dict[str, ProofExchangeNode] = {}
        for item in nodes:
            if not isinstance(item, dict):
                raise ValueError("Proof bundle node entries must be objects")

            node_id = item.get("node_id")
            cert_payload = item.get("certificate")
            depends_on = item.get("depends_on", [])

            if not isinstance(node_id, str):
                raise ValueError("Proof node field 'node_id' must be a string")
            if not isinstance(cert_payload, dict):
                raise ValueError("Proof node field 'certificate' must be an object")
            if not isinstance(depends_on, list) or not all(isinstance(v, str) for v in depends_on):
                raise ValueError("Proof node field 'depends_on' must be list[str]")

            certificate = ProofCertificate.from_dict({str(k): v for k, v in cert_payload.items()})
            parsed_nodes[node_id] = ProofExchangeNode(
                node_id=node_id,
                certificate=certificate,
                depends_on=tuple(depends_on),
            )

        return cls(schema_version=schema_version, nodes=parsed_nodes, roots=tuple(roots))

    @classmethod
    def from_json(cls, raw_json: str) -> "ProofBundle":
        """Deserialize bundle from JSON string."""
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid proof bundle JSON") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Proof bundle JSON must be an object")

        normalized = {str(key): value for key, value in parsed.items()}
        return cls.from_dict(normalized)


@dataclass(frozen=True)
class ProofExchangeResult:
    """Verification result for a received proof bundle."""

    valid_bundle: bool
    complete: bool
    invalid_nodes: list[str]
    missing_dependencies: list[str]


def create_proof_bundle(
    nodes: dict[str, ProofCertificate],
    dependencies: dict[str, list[str]] | None = None,
    roots: list[str] | None = None,
) -> ProofBundle:
    """Create a versioned proof bundle for exchange."""
    deps = dependencies or {}
    root_ids = tuple(roots or list(nodes.keys()))

    parsed_nodes: dict[str, ProofExchangeNode] = {}
    for node_id, certificate in nodes.items():
        parsed_nodes[node_id] = ProofExchangeNode(
            node_id=node_id,
            certificate=certificate,
            depends_on=tuple(deps.get(node_id, [])),
        )

    return ProofBundle(
        schema_version=SCHEMA_VERSION,
        nodes=parsed_nodes,
        roots=root_ids,
    )


def verify_proof_bundle(bundle: ProofBundle) -> ProofExchangeResult:
    """Verify exchanged proof bundle including partial-bundle status."""
    if bundle.schema_version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported proof bundle schema version '{bundle.schema_version}'")

    invalid_nodes: list[str] = []
    missing_dependencies: list[str] = []

    for node_id, node in bundle.nodes.items():
        for dep in node.depends_on:
            if dep not in bundle.nodes:
                missing_dependencies.append(f"{node_id}->{dep}")

        try:
            if not verify_certificate(node.certificate):
                invalid_nodes.append(node_id)
        except Exception:
            invalid_nodes.append(node_id)

    valid_bundle = len(invalid_nodes) == 0
    complete = len(missing_dependencies) == 0

    return ProofExchangeResult(
        valid_bundle=valid_bundle,
        complete=complete,
        invalid_nodes=sorted(invalid_nodes),
        missing_dependencies=sorted(missing_dependencies),
    )
