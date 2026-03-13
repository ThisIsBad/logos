# API Stability Contract

Version: 1.0 | Effective from: v0.2.0

---

## Stability Tiers

Every symbol exported from `logic_brain` is assigned to one of three tiers.
The tier determines the guarantees you get when upgrading between releases.

### Tier 1 — Stable

**Guarantee:** No breaking changes within a major version (`0.x` series counts as pre-1.0; see Semver Rules below). Any planned removal or signature change will go through the Deprecation Policy.

| Export | Module | Description |
|---|---|---|
| `verify` | `parser` | Verify a string-based argument |
| `parse_argument` | `parser` | Parse argument string into `Argument` |
| `parse_expression` | `parser` | Parse expression string into `LogicalExpression` |
| `is_tautology` | `parser` | Check if expression is a tautology |
| `is_contradiction` | `parser` | Check if expression is a contradiction |
| `are_equivalent` | `parser` | Check if two expressions are equivalent |
| `ParseError` | `parser` | Exception for parse failures |
| `Proposition` | `models` | Atomic proposition |
| `LogicalExpression` | `models` | Compound expression |
| `Connective` | `models` | Enum of logical connectives |
| `Argument` | `models` | Premises + conclusion |
| `VerificationResult` | `models` | Verification outcome |
| `PropositionalVerifier` | `verifier` | Z3-backed propositional verifier |
| `Variable` | `predicate_models` | FOL variable |
| `Constant` | `predicate_models` | FOL constant |
| `Predicate` | `predicate_models` | FOL predicate |
| `PredicateConnective` | `predicate_models` | Enum of FOL connectives |
| `PredicateExpression` | `predicate_models` | FOL compound expression |
| `QuantifiedExpression` | `predicate_models` | Quantified FOL expression |
| `Quantifier` | `predicate_models` | Enum (FORALL, EXISTS) |
| `FOLArgument` | `predicate_models` | FOL argument |
| `PredicateVerifier` | `predicate` | Z3-backed FOL verifier |

### Tier 2 — Provisional

**Guarantee:** Functional and tested, but details may change between minor versions. Changes will be documented in `CHANGELOG.md`. No silent removals — at minimum a changelog entry.

| Export | Module | Description |
|---|---|---|
| `LeanSession` | `lean_session` | Lean 4 interactive proof session |
| `TacticResult` | `lean_session` | Result of applying a tactic |
| `is_lean_available` | `lean_session` | Check if Lean 4 is installed |
| `Z3Session` | `z3_session` | Incremental Z3 solving session |
| `CheckResult` | `z3_session` | Result of a satisfiability check |
| `Diagnostic` | `diagnostics` | Structured error diagnostic |
| `ErrorType` | `diagnostics` | Enum of error categories |
| `LeanDiagnosticParser` | `diagnostics` | Parser for Lean error output |
| `Z3DiagnosticParser` | `diagnostics` | Parser for Z3 error output |
| `ProblemGenerator` | `generator` | Fresh logic problem generator |
| `GeneratorConfig` | `generator` | Configuration for problem difficulty |

### Tier 3 — Internal

**No stability guarantee.** These modules are importable but not part of the public API. They may change or be removed without notice.

| Module | Description |
|---|---|
| `analyzer` | Error pattern analysis |
| `evaluate` | LLM evaluation script |
| `external` | External benchmark adapters |
| `generator` | Problem generation (presets `EASY`/`MEDIUM`/`HARD`/`EXTREME` are internal) |
| `lean_verifier` | Non-interactive Lean verification |
| `loader` | Benchmark JSON loader |
| `runner` | Benchmark runner |

Within `parser.py`, the classes `Lexer`, `Parser`, and `Token` are implementation details. Do not import them directly.

---

## Semver Rules

LogicBrain follows [Semantic Versioning](https://semver.org/) with the following clarifications for the pre-1.0 period:

| Change Type | Version Bump | Example |
|---|---|---|
| Bug fix, no API change | Patch (`0.1.x`) | Fix incorrect rule identification |
| New export or optional parameter | Minor (`0.x.0`) | Add `ProblemGenerator` to `__all__` |
| Remove/rename Tier 1 export | Minor (`0.x.0`) + Deprecation Policy | Rename `verify` to `check` |
| Remove/rename Tier 2 export | Minor (`0.x.0`) + Changelog entry | Change `CheckResult` fields |
| Change Tier 3 internals | Patch (`0.1.x`) | Refactor `loader.py` |

**Pre-1.0 rule:** During the `0.x` series, minor version bumps (`0.x.0`) may contain breaking changes to Tier 1 exports, but only after the Deprecation Policy has been followed. Once `1.0.0` is released, Tier 1 breaking changes require a major version bump.

---

## Deprecation Policy

When a Tier 1 or Tier 2 symbol needs to change:

1. **Announce:** Add a `DeprecationWarning` via `warnings.warn()` in the current release.
2. **Document:** Note the deprecation in `CHANGELOG.md` with the planned removal version.
3. **Grace period:** The deprecated symbol must remain functional for at least one minor release.
4. **Remove:** Remove in the next minor release (or later). Document in `CHANGELOG.md`.

Example timeline:
- `v0.1.3`: `verify()` deprecated, `check_argument()` added. `verify()` still works, emits warning.
- `v0.1.4` (or later): `verify()` removed.

---

## What Counts as a Breaking Change

**Breaking (requires Deprecation Policy for Tier 1):**
- Removing an export from `__all__`
- Renaming a function, class, or method
- Changing required parameters of a function/method
- Changing the type of a return value
- Removing a field from a dataclass

**Not breaking:**
- Adding a new export to `__all__`
- Adding an optional parameter with a default value
- Adding a field to a dataclass with a default value
- Fixing a bug that changes behavior to match documentation
- Changing Tier 3 internals

---

## Downstream Integration Contract

If you integrate LogicBrain into an agent or tool:

1. **Import only from `logic_brain`** — e.g., `from logic_brain import verify`. Do not import from submodules directly (e.g., `from logic_brain.parser import Lexer`).
2. **Check the tier** of each symbol you use. Tier 1 is safe for production. Tier 2 may change.
3. **Pin your version** in `requirements.txt` or `pyproject.toml` (e.g., `logic-brain>=0.1.3,<0.2`).
4. **Read `CHANGELOG.md`** before upgrading.

---

## References

- Public API: `logic_brain/__init__.py`
- Changelog: `CHANGELOG.md`
- Roadmap: `docs/roadmap_v013_v020.md`
