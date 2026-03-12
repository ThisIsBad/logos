# LogicBrain - TODO / Session Handoff

Stand: 2026-03-12 (nach Release `v0.1.1`)

## Aktueller Zustand

- Release `v0.1.1` ist veröffentlicht.
- Teststatus: `144 passed`.
- Roadmap-Issues `#1` bis `#5` sind geschlossen.
- Working tree war beim letzten Check sauber.

## Was in dieser Session fertig wurde

1. CLI für `python -m logic_brain` mit `--json` und `--explain`
2. Strukturierte Diagnostik in Lean/Z3-Flows ausgebaut
3. Property-based/Fuzz-Tests mit Hypothesis ergänzt
4. Ergebnis-Checker konsolidiert (`tools/check_results.py`)
5. Beispiele + Notebook ergänzt (`examples/`)
6. Extensions-Assessment dokumentiert (`docs/logic_extensions_assessment.md`)
7. Packaging-Fix für `pip install -e ".[dev]"`
8. Changelog + Version Bump + GitHub Release erstellt

## Prios für die nächste Session

### P1 - CI einführen (empfohlen als nächster Schritt)
- [ ] GitHub Actions Workflow hinzufügen (`.github/workflows/ci.yml`)
- [ ] Matrix mindestens auf Python 3.10/3.11
- [ ] Steps: Install, `pip install -e ".[dev]"`, `pytest -q`
- [ ] Optional: getrennte Jobs für lint/type-check vorbereiten

### P2 - Tooling konsolidieren (restliche Alt-Skripte)
- [ ] `check_lean.py` und `check_predicate.py` in `tools/` überführen
- [ ] API/CLI der Tools vereinheitlichen
- [ ] README-Kommandos vollständig auf `tools/`-Pfade angleichen

### P3 - Release-Prozess härten
- [ ] Kleines Release-Playbook in `docs/` (Tagging, Notes, Verify-Checklist)
- [ ] Optional: automatisierte Release Notes via `gh release create --generate-notes`

## Referenzen

- Changelog: `CHANGELOG.md`
- Vision/Roadmap: `vision_and_roadmap.md`
- Extensions-Assessment: `docs/logic_extensions_assessment.md`
- Releases: `https://github.com/ThisIsBad/LogicBrain/releases`
