# Changelog

All notable changes to this project are documented in this file.

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
