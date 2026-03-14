# Metamorphic Relation Ledger

Version: 1.0  
Status: Active

This ledger tracks metamorphic relations (MRs) as versioned "super-axioms" for
regression safety. Every MR entry must point to executable tests.

## Risk Taxonomy

- `core-semantics`: logical soundness of verification outcomes.
- `parser-robustness`: stability under syntax-preserving input transformations.
- `session-safety`: state and satisfiability invariants in incremental solving.

## Entry Schema

Each MR entry should include:

- `id`: stable identifier (e.g. `MR-V01`)
- `title`: short descriptive name
- `module`: primary module under test
- `risk_level`: one of the taxonomy values above
- `transform`: source -> transformed input relation
- `expected_relation`: invariant that must hold
- `tolerance`: exact, approximate, or bounded (with details)
- `status`: active, pending, deprecated
- `test_refs`: concrete pytest node references

## Seed Entries (MR-1..MR-3)

| id | title | module | risk_level | transform | expected_relation | tolerance | status | test_refs |
|---|---|---|---|---|---|---|---|---|
| MR-V01 | Implication rewrite (MP) | `verifier` | core-semantics | `A -> B` -> `(~A | B)` in premise | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_verifier.py::test_metamorphic_relations_preserve_validity[implication-rewrite-mp]` |
| MR-V02 | Implication rewrite (MT) | `verifier` | core-semantics | `A -> B` -> `(~A | B)` in premise | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_verifier.py::test_metamorphic_relations_preserve_validity[implication-rewrite-mt]` |
| MR-V03 | Double negation elimination | `verifier` | core-semantics | `~~A` -> `A` | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_verifier.py::test_metamorphic_relations_preserve_validity[double-negation-elim]` |
| MR-V04 | De Morgan conjunction form | `verifier` | core-semantics | `~(A & B)` -> `(~A | ~B)` | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_verifier.py::test_metamorphic_relations_preserve_validity[de-morgan-and]` |
| MR-P01 | Whitespace invariance | `parser` | parser-robustness | normalize spacing/newlines | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[whitespace-padding]`, `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[newline-premise-break]` |
| MR-P02 | Parentheses invariance (safe) | `parser` | parser-robustness | add redundant parentheses | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[parentheses-redundant]`, `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[parentheses-unary-binary]` |
| MR-P03 | Operator alias invariance | `parser` | parser-robustness | `->/=>`, `<->/<=>`, `~/!`, `&/^` | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[alias-imp-not]`, `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[alias-iff]`, `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[alias-and]` |
| MR-P04 | Premise order invariance | `parser` | parser-robustness | reorder comma-separated premises | `verify(...).valid` unchanged | exact | active | `tests/test_metamorphic_parser.py::test_parser_metamorphic_relations_preserve_outcome[premise-order]` |
| MR-Z01 | Push/pop restoration | `z3_session` | session-safety | add contradictory scope then `pop()` | baseline satisfiability restored | exact | active | `tests/test_metamorphic_z3_session.py::test_mr_push_pop_restores_baseline_sat` |
| MR-Z02 | Constraint order invariance (SAT/UNSAT) | `z3_session` | session-safety | reorder independent / contradictory constraints | `check().status` and `satisfiable` unchanged | exact | active | `tests/test_metamorphic_z3_session.py::test_mr_reordering_independent_constraints_preserves_sat`, `tests/test_metamorphic_z3_session.py::test_mr_reordering_contradictory_constraints_preserves_unsat` |
| MR-Z03 | Integer bound equivalence | `z3_session` | session-safety | `x > 5` <-> `x >= 6` | sat classification unchanged | exact | active | `tests/test_metamorphic_z3_session.py::test_mr_equivalent_integer_bounds_preserve_classification` |
| MR-Z04 | Reset-to-fresh equivalence | `z3_session` | session-safety | `reset(); redeclare; reassert` | behaves like fresh session | exact | active | `tests/test_metamorphic_z3_session.py::test_mr_reset_clears_state_and_redeclaration_behaves_like_fresh_session` |
| MR-C01 | Certificate roundtrip invariance (propositional) | `certificate` | core-semantics | `cert` -> `ProofCertificate.from_json(cert.to_json())` | `verify_certificate` result unchanged | exact | active | `tests/test_metamorphic_certificate.py::test_mr_certificate_json_roundtrip_preserves_verification_state_propositional` |
| MR-C02 | Certificate roundtrip invariance (z3 session) | `certificate` | session-safety | `cert` -> `ProofCertificate.from_json(cert.to_json())` | `verify_certificate` result unchanged | exact | active | `tests/test_metamorphic_certificate.py::test_mr_certificate_json_roundtrip_preserves_verification_state_z3_session` |

## Maintenance Rule

When a metamorphic test is added, changed, or removed:

1. Update/add the corresponding ledger entry in this file.
2. Keep `test_refs` accurate and executable.
3. Reflect status changes (`active`, `pending`, `deprecated`).
