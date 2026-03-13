# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [0.2.0] - 2026-03-13

First release with an explicit API stability contract. Agent developers can
rely on Tier 1/2 exports per `STABILITY.md`.

### Added
- **`STABILITY.md`** — API stability contract with 3-tier classification (Stable / Provisional / Internal), semver rules, and deprecation policy.
- **`examples/agent_integration.py`** — Copy-paste-ready example showing full agent workflow: verify arguments, generate problems, Z3 sessions, diagnostics, and Lean proofs.
- **`py.typed` marker** — PEP 561 compliance for downstream type-checking.
- **`ProblemGenerator` and `GeneratorConfig`** exported from `logic_brain` (Tier 2 — Provisional).
- **API reference** generated via pdoc at `docs/api/`.
- **32 new tests** for `generator`, `analyzer`, `external`, and `lean_verifier` modules (total: 185+).
- **ruff linting** in CI pipeline.
- **Python 3.12** in CI test matrix.
- **Benchmark regression gate** (`tools/check_results.py exam`) in CI.
- `__all__` defined in 8 internal modules; internal parser classes prefixed with `_`.
- `schema_version` field on `Diagnostic` dataclass.

### Changed
- Internal parser classes renamed: `Token` → `_Token`, `Lexer` → `_Lexer`, `Parser` → `_Parser`.
- Broad `except Exception` narrowed to specific types in `predicate.py` and `lean_verifier.py`.
- `z3-solver` dependency pinned to `>=4.12,<5.0`.
- `pdoc` added to dev dependencies.
- `README.md` updated with new project structure, agent integration section, and API reference link.

### Removed
- 9 deprecated root-level scripts (moved to `tools/` in v0.1.2).
- Dead `SortType` enum from `z3_session.py`.
- `todo.md` replaced with pointer to `docs/roadmap_v013_v020.md`; original archived to `docs/archive/todo_v012.md`.

## [0.1.2] - 2026-03-13

### Added
- Safe AST-based constraint parsing in `Z3Session` (replaces `eval`) with explicit operator/function allow-listing.
- New tooling entrypoints: `tools/generate_exam.py`, `tools/generate_hardmode.py`, `tools/generate_escalation.py`, `tools/check_stress_results.py`, `tools/check_fol_results.py`.
- Additional Z3 session tests for implication operators and malformed/unsupported syntax handling.

### Changed
- `tools/check_predicate_results.py` now acts as a legacy wrapper and forwards to `tools/check_fol_results.py`.
- Root scripts `generate_exam.py`, `hardmode.py`, `escalate.py`, `verify_stress.py` now act as deprecated wrappers to `tools/` commands.
- README and release playbook now document canonical `tools/` flows for generation and checking (including FOL and stress).

## [0.1.1] - 2026-03-12

### Added
- CLI entrypoint via `python -m logic_brain` with `--json` and `--explain` output modes.
- Structured diagnostics exports in public API (`Diagnostic`, `ErrorType`, parser helpers).
- Property-based and fuzz testing with Hypothesis.
- Example scripts in `examples/` and notebook demo in `examples/logic_brain_demo.ipynb`.
- Extension feasibility document at `docs/logic_extensions_assessment.md`.

### Changed
- `Z3Session` now provides structured diagnostics for unsat/unknown and parse failures.
- Improved parser and diagnostics coverage with additional tests.
- Consolidated result checking scripts into `tools/check_results.py`.

### Fixed
- Editable install (`pip install -e ".[dev]"`) by constraining setuptools package discovery.
