# LogicBrain Roadmap v0.1.3 – v0.2.0

Stand: 2026-03-13 | Basis: `claude_opus_planning_brief.md` + Repo-Analyse auf v0.1.2

---

## Kernthese

Das Hauptproblem ist nicht mehr "mehr Features bauen", sondern **Priorisieren + Produktisieren**.

LogicBrain ist technisch solide. Der gesamte Wert der Library liegt im Versprechen "deterministisch und korrekt". Dieses Versprechen muss jetzt durch Stabilitaetsvertrag, Coverage, CI-Gates und ein funktionierendes Integrationsbeispiel untermauert werden — nicht durch mehr Features.

**Reihenfolge: Stabilisieren → Messbar machen → Integrierbar machen → Dann erweitern.**

---

## Phase 1: API Stabilization (v0.1.3) — 2-3 Wochen

**Outcome:** Die Agent-Facing API hat einen klaren Vertrag. Integratoren koennen sich auf stabile Interfaces verlassen.

| Task | Beschreibung |
|---|---|
| API-Vertrag definieren | `STABILITY.md` — Tier 1-3 = stable, Tier 4-5 = provisional. Semver-Regeln klar dokumentiert. |
| Deprecation-Policy | Mindestens 1 Minor-Version Vorlaufzeit fuer Breaking Changes. `warnings.warn` mit `DeprecationWarning`. |
| Interne Klassen abgrenzen | `Lexer`, `Parser`, `Token` in `parser.py` mit `_`-Prefix versehen. Module-Level `__all__` fuer interne Module. |
| Diagnostics-Schema versionieren | `Diagnostic` bekommt ein `schema_version: str` Feld. Agenten koennen darauf filtern. |
| Root-Cleanup | Deprecated Root-Skripte entfernen oder nach `tools/legacy/` verschieben. |
| vision_and_roadmap.md aktualisieren | Erledigte Phasen kuerzen, aktuelle Realitaet (v0.1.2) abbilden. |
| todo.md ersetzen | Durch dieses Dokument ersetzen. `todo.md` archivieren. |

## Phase 2: Quality & Observability (v0.1.4) — 2-3 Wochen

**Outcome:** Messbare Qualitaetsgarantien. CI blockt Regressionen automatisch.

| Task | Beschreibung |
|---|---|
| Test-Coverage schliessen | Tests fuer `generator.py`, `analyzer.py`, `external.py`, `lean_verifier.py`. Ziel: jedes Modul mind. 1 direkter Testfile. |
| CI haerten | Ruff-Linting, mypy strict, Coverage-Report (Threshold 85%), Python 3.12 in Matrix. |
| Benchmark-CI-Gate | `tools/check_results.py exam` als CI-Step. Fail bei Score-Regression. |
| Broad Exception Handling fixen | `predicate.py:144` und `lean_verifier.py:83` — spezifische Exceptions statt `Exception`. |
| Dead Code entfernen | `SortType` enum, `lean_verifier.py` konsolidieren oder klar abgrenzen. |
| Type-Inkonsistenzen beheben | `Argument.premises` vs `FOLArgument.premises` (`list` vs `tuple`) aufloesen. |

## Phase 3: Integration & Documentation (v0.2.0) — 3-4 Wochen

**Outcome:** Ein externer Agent-Entwickler kann LogicBrain in <30 Minuten integrieren. v0.2.0 ist das erste "stable" Release.

| Task | Beschreibung |
|---|---|
| Minimales Integrationsbeispiel | `examples/agent_integration.py` — vollstaendiges Beispiel wie Claude Code / OpenCode LogicBrain als Tool nutzt. |
| `py.typed` Marker | PEP 561 compliance fuer Downstream-Type-Checking. |
| API-Referenz generieren | Automatisch aus Docstrings (pdoc oder mkdocstrings). Hosted via GitHub Pages. |
| `ProblemGenerator` exportieren | In `__all__` aufnehmen — Agenten wollen ggf. frische Probleme generieren. |
| v0.2.0 Release | Erstes Release mit explizitem Stabilitaetsversprechen fuer Tier 1-3 API. |

---

## KPIs

| KPI | Aktuell | Ziel v0.1.4 | Ziel v0.2.0 | Messmethode |
|---|---|---|---|---|
| **Test Count** | 153 | 180+ | 200+ | `pytest --co -q` |
| **Test Coverage** | unbekannt | ≥85% | ≥90% | `pytest --cov` in CI |
| **Module mit direkten Tests** | 11/17 | 15/17 | 17/17 | Glob `tests/test_*.py` vs `logic_brain/*.py` |
| **CI Pipeline-Dauer** | ~90s | <120s | <120s | GitHub Actions Timing |
| **Linting-Fehler** | unbekannt | 0 | 0 | ruff in CI |
| **mypy strict Fehler** | unbekannt | 0 | 0 | mypy in CI |
| **Benchmark-Score (Exam)** | Baseline TBD | ≥ Baseline | ≥ Baseline | `tools/check_results.py exam` in CI |
| **Time-to-Integration** | unbekannt | — | <30 min | Manueller Test mit frischem Checkout |
| **API-Breaking-Changes ohne Deprecation** | n/a | 0 | 0 | Review-Policy |
| **Root-Level Clutter** | 9 Skripte | ≤3 | 0 | Root `*.py` Dateien |

---

## Issue-Vorschlaege

### Issue #1: API Stability Contract (STABILITY.md)

**Prioritaet:** P0 (Blocker fuer v0.1.3)

**Akzeptanzkriterien:**
- [ ] `STABILITY.md` existiert im Repo-Root
- [ ] Alle 30 Exports aus `__all__` sind einem Stability-Tier zugeordnet (stable / provisional / internal)
- [ ] Semver-Regeln dokumentiert: was ist breaking, was ist minor, was ist patch
- [ ] Deprecation-Policy: mindestens 1 Minor-Version Vorlauf, `DeprecationWarning` Pflicht
- [ ] Diagnostics-Schema bekommt `schema_version` Feld
- [ ] README verlinkt auf STABILITY.md

### Issue #2: Interne API-Grenzen schaerfen

**Prioritaet:** P1

**Akzeptanzkriterien:**
- [ ] `Lexer`, `Parser`, `Token` in `parser.py` mit `_`-Prefix umbenannt
- [ ] Alle internen Module (`analyzer`, `evaluate`, `external`, `generator`, `lean_verifier`, `loader`, `runner`) definieren eigenes `__all__`
- [ ] Kein Breaking Change fuer bestehende `from logic_brain import X` Imports

### Issue #3: Test Coverage Gaps schliessen

**Prioritaet:** P1

**Akzeptanzkriterien:**
- [ ] `tests/test_generator.py` — mind. 5 Tests (Presets, Seed-Determinismus, Edge Cases)
- [ ] `tests/test_analyzer.py` — mind. 3 Tests (Report, Markdown-Output, leere Inputs)
- [ ] `tests/test_external.py` — mind. 2 Tests (SATBench/FOLIO Loader mit Fixture-Daten)
- [ ] `tests/test_lean_verifier.py` — mind. 2 Tests (conditional auf Lean-Verfuegbarkeit)
- [ ] `pytest --cov` zeigt ≥85% Gesamtcoverage
- [ ] CI-Step fuer Coverage mit Threshold

### Issue #4: CI Pipeline haerten

**Prioritaet:** P1

**Akzeptanzkriterien:**
- [ ] ruff-Linting als CI-Step (0 Fehler)
- [ ] mypy strict als CI-Step (0 Fehler)
- [ ] Coverage-Report als CI-Artefakt
- [ ] Python 3.12 in CI-Matrix
- [ ] `tools/check_results.py exam` als CI-Step (Benchmark-Regression-Gate)
- [ ] CI-Dauer bleibt unter 3 Minuten

### Issue #5: Root-Verzeichnis aufraeumen + Doku aktualisieren

**Prioritaet:** P2

**Akzeptanzkriterien:**
- [ ] `debug_fol09.py`, `test_lean.py`, `test_z3_09.py` entfernt
- [ ] Root-Wrapper (`check_lean.py`, `check_predicate.py`, `generate_exam.py`, `hardmode.py`, `escalate.py`, `verify_stress.py`) entfernt — `tools/` ist kanonisch
- [ ] `vision_and_roadmap.md` aktualisiert
- [ ] `todo.md` archiviert nach `docs/archive/todo_v012.md`
- [ ] Root enthaelt max. 3 `.py`-Dateien

### Issue #6: Exception Handling & Dead Code Cleanup

**Prioritaet:** P2

**Akzeptanzkriterien:**
- [ ] `predicate.py:144` — `except Exception` durch spezifische Exceptions ersetzt
- [ ] `lean_verifier.py:83` — analog
- [ ] `SortType` enum in `z3_session.py` entfernt oder genutzt
- [ ] `lean_verifier.py` konsolidiert oder klar abgegrenzt
- [ ] `Argument.premises` vs `FOLArgument.premises` Typ-Inkonsistenz aufgeloest

### Issue #7: Minimales Agent-Integrationsbeispiel

**Prioritaet:** P1 (Blocker fuer v0.2.0)

**Akzeptanzkriterien:**
- [ ] `examples/agent_integration.py` existiert
- [ ] Zeigt vollstaendigen Workflow: Problem generieren, verifizieren, Session nutzen, Diagnostik auswerten
- [ ] Funktioniert als Copy-Paste-Vorlage fuer Claude Code / OpenCode
- [ ] Enthaelt Kommentare, die Agent-Entscheidungspunkte markieren
- [ ] README verlinkt darauf

---

## Risikoanalyse

| # | Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **API-Bruch ohne Warnung** — Refactoring aendert Public API, bricht Agent-Integrationen. Kein Vertrag verhindert das. | Hoch | Hoch | STABILITY.md + `__all__` als Vertrag. CI-Test der alle Exports prueft. Deprecation-Warnings statt stille Aenderungen. |
| R2 | **Lean-Abhaengigkeit als Deployment-Blocker** — Lean 4 schwer installierbar, Tests in CI uebersprungen. | Mittel | Mittel | Lean bleibt optional. Kein Import-Fehler ohne Lean. Klare Doku "Lean ist optional". |
| R3 | **Feature-Creep durch Logik-Erweiterungen** — Modal/Temporal/Many-valued zu frueh, destabilisiert Kern-API. | Mittel | Hoch | Erst v0.2.0 (stabile API), dann Erweiterungen. Hinter eigenen Modulen/Klassen. |
| R4 | **Bus-Faktor 1** — Ein Maintainer, keine externen Contributors sichtbar. | Hoch | Mittel | Integrationsbeispiel + API-Doku senkt Einstiegshuerde. `CONTRIBUTING.md` anlegen. |
| R5 | **Z3 Binding Breaking Changes** — `z3-solver>=4.12` unpinned. | Niedrig | Mittel | Version-Cap (`<5.0`). Z3-Integrationstests als Regression-Gate. |

---

## Bewusst NICHT tun (naechste 6-8 Wochen)

1. **Keine Modal/Temporal/Many-valued Logik.** Erst API stabilisieren, dann erweitern. Jede Stunde in neue Logik-Systeme fehlt bei der Produktisierung.

2. **Keinen Lemma-Cache (Phase 4 alte Roadmap).** Setzt aktive LeanSession-Nutzung durch Agenten voraus. Die gibt es noch nicht.

3. **Kein PyPI-Release.** Erst wenn API-Vertrag und CI stehen. Ein `pip install logic-brain` das nach dem naechsten Release bricht ist schlimmer als kein PyPI.

4. **Keine Web-API / REST-Server.** LogicBrain als Python-Library im Agent-Prozess ist der richtige Scope. HTTP-Layer bringt Latenz, Deployment-Komplexitaet, Sicherheitsfragen — ohne heutigen Nutzer.

5. **Keine MCTS/Baumsuche in LogicBrain.** Agent entscheidet, LogicBrain verifiziert. Suchstrategien gehoeren in den Agent.

6. **Kein Over-Engineering der Diagnostik.** Das aktuelle System ist gut genug. Erst beweisen, dass Agenten die bestehenden Diagnostics nutzen, dann iterieren.

---

## Referenzen

- Vision & Architektur: `vision_and_roadmap.md`
- Changelog: `CHANGELOG.md`
- Release Playbook: `docs/release_playbook.md`
- Extensions Assessment: `docs/logic_extensions_assessment.md`
- Planning Brief: `docs/claude_opus_planning_brief.md`
- Archiviertes Session-Log: `docs/archive/todo_v012.md`
