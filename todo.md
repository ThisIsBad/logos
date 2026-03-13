# LogicBrain - TODO / Session Handoff

Stand: 2026-03-12 (nach Release `v0.1.1`)

## Aktueller Zustand

- Release `v0.1.1` ist veroffentlicht.
- Teststatus: `144 passed`.
- Roadmap-Issues `#1` bis `#5` sind geschlossen.
- Fokus laut Roadmap: CI + Tooling-Konsolidierung.

## Arbeitsmodus fur die nachste Stunde

Ziel: In einem 60-Minuten-Sprint die Roadmap-Punkte so weit umsetzen,
dass das Repo wartbarer ist und ohne manuelle Schritte getestet werden kann.

### Operative Annahmen (damit autonom gearbeitet werden kann)

- Python-Versionen fur CI: `3.10` und `3.11`.
- Testkommando: `pytest -q`.
- Installationsweg: `pip install -e ".[dev]"`.
- Legacy-Skripte im Repo bleiben vorerst erhalten, werden aber auf neue Tools verwiesen.
- Kein Release/Tagging in dieser Stunde, nur Vorbereitung.

---

## Sprint-Backlog (aus der Roadmap abgeleitet)

### Phase A - CI stabilisieren (P1, hoch)

- [ ] A1: `.github/workflows/ci.yml` erstellen mit Triggern (`push`, `pull_request`).
- [ ] A2: Matrix fur Python `3.10` und `3.11` konfigurieren.
- [ ] A3: Workflow-Schritte definieren: Checkout, Setup Python, Install, Tests.
- [ ] A4: `pip install -e ".[dev]"` im Workflow verankern.
- [ ] A5: `pytest -q` im Workflow verankern.
- [ ] A6: Fail-fast-Verhalten fur Matrix prufen (optional `fail-fast: false` dokumentieren).
- [ ] A7: CI-Badge in `README.md` erganzen (wenn Repo-URL/Workflow-Name final ist).
- [ ] A8: Lokalen Dry-Run der relevanten Befehle durchfuhren und dokumentieren.

### Phase B - Tooling konsolidieren (P2, hoch)

- [ ] B1: Neues Tool `tools/check_lean_results.py` anlegen (CLI-kompatibel zu `tools/check_results.py`).
- [ ] B2: Neues Tool `tools/check_predicate_results.py` anlegen (ohne hartkodierte Nutzerpfade).
- [ ] B3: Gemeinsame CLI-Parameter festlegen (Dateipfade als Args, klare Defaults).
- [ ] B4: Gemeinsame Ausgabeformate vereinheitlichen (`OK/WRONG/MISS`, Score-Zeile).
- [ ] B5: Root-Skript `check_lean.py` als dunnen Wrapper oder mit Deprecation-Hinweis versehen.
- [ ] B6: Root-Skript `check_predicate.py` als dunnen Wrapper oder mit Deprecation-Hinweis versehen.
- [ ] B7: Optional: `verify_stress.py` an neues Tooling-Muster angleichen.
- [ ] B8: Optional: `generate_exam.py`/`hardmode.py`/`escalate.py` auf `logic_brain.generator` evaluieren (nur TODO/Notiz, falls nicht in Stunde schaffbar).

### Phase C - Doku und UX angleichen (P2, mittel)

- [ ] C1: `README.md` um Abschnitt "Tooling" mit aktuellen `tools/`-Kommandos erganzen.
- [ ] C2: Veraltete Root-Kommandos in README ersetzen oder als legacy markieren.
- [ ] C3: Kurze Migrationsnotiz in `CHANGELOG.md` (unreleased) vorbereiten.
- [ ] C4: In `todo.md` Status aktualisieren (erledigt/offen + nachste sinnvolle Schritte).

### Phase D - Release-Prozess harten (P3, mittel)

- [ ] D1: `docs/release_playbook.md` anlegen (Tagging, Test-Checklist, Release Notes).
- [ ] D2: Minimal-Checkliste definieren: Tests, Changelog, Version, Tag, GitHub Release.
- [ ] D3: Optionalen `gh`-Befehl fur auto-generierte Notes dokumentieren.

---

## Konkreter 60-Minuten-Plan (sequenziell)

1. **Minute 0-20:** CI-Workflow implementieren + lokal plausibilisieren.
2. **Minute 20-45:** Tooling-Konsolidierung (`tools/`-Skripte + Legacy-Wrappers).
3. **Minute 45-55:** README + ggf. Changelog aktualisieren.
4. **Minute 55-60:** Finaler Check (`pytest -q` bzw. gezielte Tests) und Session-Handoff notieren.

## Definition of Done fur diese Stunde

- CI-Workflow-Datei existiert und deckt Python 3.10/3.11 ab.
- Mindestens ein konsolidiertes Legacy-Tool in `tools/` uberfuhrt.
- README zeigt den neuen, bevorzugten Tooling-Pfad.
- Offene Restpunkte sind klar im TODO dokumentiert.

## Referenzen

- Changelog: `CHANGELOG.md`
- Vision/Roadmap: `vision_and_roadmap.md`
- Extensions-Assessment: `docs/logic_extensions_assessment.md`
- Releases: `https://github.com/ThisIsBad/LogicBrain/releases`
