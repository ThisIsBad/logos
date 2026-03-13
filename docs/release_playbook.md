# Release Playbook

This document defines the lightweight release process for LogicBrain.

## Scope

- Applies to tagged releases (for example `v0.1.2`).
- Assumes maintainers have push access and `gh` CLI authentication.

## Pre-Release Checklist

Run from the repository root:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python tools/check_results.py exam
python tools/check_fol_results.py
python tools/check_stress_results.py
```

Optional if Lean is installed:

```powershell
python tools/check_lean_results.py --lean-bin "C:\Users\<user>\.elan\bin\lean.exe"
```

## Version and Changelog

1. Update version in `pyproject.toml`.
2. Add release notes to `CHANGELOG.md`.
3. Ensure README commands and docs match current tooling.

## Tag and Release

1. Create a release commit.
2. Create and push tag:

```powershell
git tag vX.Y.Z
git push origin vX.Y.Z
```

3. Create GitHub release.

### Option A: Auto-generated notes (recommended)

```powershell
gh release create vX.Y.Z --generate-notes
```

### Option B: Manual notes

```powershell
gh release create vX.Y.Z --title "vX.Y.Z" --notes "See CHANGELOG.md"
```

## Verification Checklist

- Tag exists remotely.
- GitHub release entry exists and has notes.
- CI workflow passed on tag or release commit.
- `pip install -e ".[dev]"` still works on a clean checkout.
- Core smoke tests still pass (below).

## Smoke-Test Matrix

Run these quick checks before or after release:

```powershell
# Core parser/verifier API sanity
python -c "from logic_brain import verify; r=verify('P -> Q, P |- Q'); print(r.valid, r.rule)"

# CLI sanity
python -m logic_brain "P -> Q, P |- Q" --json

# Benchmark checker sanity
python tools/check_results.py exam

# Predicate checker sanity
python tools/check_fol_results.py

# Stress checker sanity
python tools/check_stress_results.py
```

If Lean is available:

```powershell
python tools/check_lean_results.py --lean-bin "C:\Users\<user>\.elan\bin\lean.exe"
```
