"""Metamorphic tests for propositional verifier semantics (Issue #27)."""

from __future__ import annotations

import pytest

from logic_brain import verify


def _assert_same_validity(source_argument: str, transformed_argument: str) -> None:
    source = verify(source_argument)
    transformed = verify(transformed_argument)

    assert transformed.valid is source.valid, (
        "Metamorphic relation violated:\n"
        f"  source:      {source_argument} -> valid={source.valid}\n"
        f"  transformed: {transformed_argument} -> valid={transformed.valid}"
    )


@pytest.mark.parametrize(
    ("source_argument", "transformed_argument"),
    [
        # Implication rewrite: (A -> B)  <=>  (~A | B)
        ("P -> Q, P |- Q", "(~P | Q), P |- Q"),
        ("R -> S, ~S |- ~R", "(~R | S), ~S |- ~R"),
        # Double negation
        ("~~P |- P", "P |- P"),
        ("P |- ~~P", "P |- P"),
        # Commutativity
        ("P & Q |- Q & P", "Q & P |- P & Q"),
        ("P |- P | Q", "P |- Q | P"),
        # Associativity
        ("(P & Q) & R |- P & (Q & R)", "P & (Q & R) |- (P & Q) & R"),
        ("(P | Q) | R, ~P, ~Q |- R", "P | (Q | R), ~P, ~Q |- R"),
        # De Morgan rewrites
        ("~(P & Q), P |- ~Q", "(~P | ~Q), P |- ~Q"),
        ("~(P | Q), P |- ~Q", "(~P & ~Q), P |- ~Q"),
    ],
)
def test_metamorphic_relations_preserve_validity(
    source_argument: str,
    transformed_argument: str,
) -> None:
    _assert_same_validity(source_argument, transformed_argument)
