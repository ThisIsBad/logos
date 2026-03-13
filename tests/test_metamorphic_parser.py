"""Metamorphic parser tests for syntax-preserving transformations (Issue #25)."""

from __future__ import annotations

import pytest

from logic_brain import verify


def _assert_same_outcome(source_argument: str, transformed_argument: str) -> None:
    source = verify(source_argument)
    transformed = verify(transformed_argument)

    assert transformed.valid is source.valid, (
        "Parser metamorphic relation violated:\n"
        f"  source:      {source_argument} -> valid={source.valid}\n"
        f"  transformed: {transformed_argument} -> valid={transformed.valid}"
    )


@pytest.mark.parametrize(
    ("source_argument", "transformed_argument"),
    [
        # Whitespace and line-break invariance
        ("P -> Q, P |- Q", "   P   ->   Q  ,   P   |-   Q   "),
        ("P -> Q, Q |- P", "P -> Q,\nQ |- P"),
        # Parentheses insertion/removal where precedence stays equivalent
        ("P -> Q, P |- Q", "((P -> Q)), (P) |- (Q)"),
        ("~P & Q |- Q", "(~P) & (Q) |- (Q)"),
        # Operator alias equivalence
        ("P -> Q, ~Q |- ~P", "P => Q, !Q |- !P"),
        ("P <-> Q |- Q <-> P", "P <=> Q |- Q <=> P"),
        ("P & Q |- P", "P ^ Q |- P"),
        # Premise ordering invariance
        ("P -> Q, P, R |- Q", "R, P, P -> Q |- Q"),
    ],
)
def test_parser_metamorphic_relations_preserve_outcome(
    source_argument: str,
    transformed_argument: str,
) -> None:
    _assert_same_outcome(source_argument, transformed_argument)
