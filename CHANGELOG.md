# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

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
