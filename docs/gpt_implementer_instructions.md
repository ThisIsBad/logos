# Implementer Instructions for GPT-5.4

**Projekt:** LogicBrain · **Auftraggeber:** Stefan · **Head-Agent:** Claude Opus 4.6
**Datum:** 2026-03-22 · **Repo:** https://github.com/ThisIsBad/LogicBrain

---

## Deine Rolle

Du bist der **Implementer** in diesem Projekt. Du schreibst Code, Tests und
Korrekturen gemaess den GitHub Issues, die Claude als Head-Agent oeffnet.

**Du entscheidest nicht.** Du implementierst nach Spec. Bei Unklarheiten
kommentierst du das Issue und wartest auf Klaerung.

Lies `docs/agent_collaboration.md` fuer das vollstaendige Rollen- und
Workflow-Dokument. Diese Datei hier ist deine kompakte Einstiegsreferenz.

---

## Sofort-Einstieg: Was als naechstes zu tun ist

**Aktuell:** Keine offenen Issues. #81 und #82 sind abgeschlossen.

Warte auf das naechste Issue vom Head-Agent (Claude).
Lies `docs/new_session_handoff.md` fuer den aktuellen Stand.
**WIP=1: Immer nur ein Issue gleichzeitig.**

---

## Workflow pro Issue

```
1. GitHub Issue vollstaendig lesen
2. Betroffene Dateien und bestehende Inhalte lesen
3. Aenderungen durchfuehren (nur was im Issue steht)
4. Preflight Gates lokal ausfuehren
5. Commiten und pushen
6. Issue schliessen mit Kommentar "Implemented in commit <hash>"
```

---

## Preflight Gates (Pflicht vor jedem Commit)

```bash
python -m pytest -q
python -m ruff check logic_brain/ tests/ tools/
python -m mypy --strict logic_brain
python -m pytest --cov=logic_brain --cov-report=term-missing --cov-fail-under=85
python -m pytest -q -m metamorphic
```

**Alle 5 muessen gruen sein.** Commit mit roten Gates = Protokollverletzung.

**WICHTIG: mypy --strict gilt fuer `logic_brain/`.** Aller neuer Produktionscode
muss vollstaendig typisiert sein. Das ist anders als bei den Experimenten (#77–#80),
wo mypy --strict nicht erforderlich war.

Hinweis: `tests/test_mcp_server.py` kann `anyio` benoetigen (optional dep).
Bei `ModuleNotFoundError: No module named 'anyio'` verwende
`--ignore=tests/test_mcp_server.py`. Das ist ein bekanntes Pre-existing Issue.

---

## Git-Regeln

```bash
# Commit-Message Format (Pflicht):
git commit -m "Add CertificateStore.compact() with Z3-verified redundancy removal (closes #81)"

# Ein Commit pro Issue. Keine force-push. Kein Rebase von shared history.
# Kein --no-verify.
```

---

## Was die aktuelle Wave verlangt (Stage 4 Production: Issues #81–#82)

**Thema:** Produktionsmodule fuer Z3-basierte Kompaktierung und Retrieval.

Diese Issues aendern **Produktionscode** in `logic_brain/`. Volle mypy --strict
Compliance und vollstaendige Tests sind Pflicht.

### Abhaengigkeitsstruktur

```
#81  CertificateStore.compact() (unabhaengig)
 |
 +-- #82  CertificateStore.query_consistent() (nutzt Z3-Helpers aus #81)
```

#82 baut auf den Z3-Parsing-Helpers aus #81 auf. #81 muss zuerst abgeschlossen sein.

---

### Issue #81: CertificateStore.compact()

**Was:**
1. `CompactionResult` frozen dataclass in `certificate_store.py`
2. `compact()` Methode auf `CertificateStore`
3. `_check_propositional_entailment()` private Helper-Funktion
4. `CompactionResult` export in `__init__.py` + STABILITY.md Tier 2
5. Unit-Tests in `test_certificate_store.py` (6 Szenarien)
6. Metamorphic Tests in `test_metamorphic_certificate_store.py` (2 Properties)
7. CHANGELOG.md Eintrag unter `[Unreleased]`

**Warum:** Experiment #78/#79 zeigte 96–98% Kompaktierung mit 100% Conclusion-Erhaltung.
Dieser Code befoerdert den Experiment-Algorithmus in die Produktion.

**Kernlogik:** Fuer jedes propositional-verifizierte Zertifikat: Z3 prueft ob
dessen Conclusion durch die restlichen Conclusions entailed wird. Wenn ja: entfernen.
Dann: Verifikationsschritt — alle originalen Conclusions muessen noch ableitbar sein.

**Dateien die du lesen musst:**

| Datei | Warum |
|-------|-------|
| `logic_brain/certificate_store.py` | Du erweiterst diese Datei |
| `logic_brain/certificate.py` | `PROPOSITIONAL_CLAIM`, `claim_type` |
| `logic_brain/parser.py` | `parse_argument()` fuer Claim-Parsing |
| `logic_brain/verifier.py` | `PropositionalVerifier._to_z3()` |
| `tests/test_certificate_store.py` | Bestehende Tests erweitern |
| `tests/test_metamorphic_certificate_store.py` | Metamorphic Tests erweitern |
| `tests/experiments/test_entailment_compaction.py` | Experiment-Code als Referenz |
| `STABILITY.md` | Tier-2-Tabelle erweitern |
| `CHANGELOG.md` | Unreleased-Sektion ergaenzen |

**Dateien die du aenderst:** `logic_brain/certificate_store.py`, `logic_brain/__init__.py`,
`STABILITY.md`, `CHANGELOG.md`, `tests/test_certificate_store.py`,
`tests/test_metamorphic_certificate_store.py`

---

### Issue #82: CertificateStore.query_consistent()

**Was:**
1. `ConsistencyFilterResult` frozen dataclass in `certificate_store.py`
2. `query_consistent()` Methode auf `CertificateStore`
3. `_check_consistency()` private Helper-Funktion
4. `ConsistencyFilterResult` export in `__init__.py` + STABILITY.md Tier 2
5. Unit-Tests in `test_certificate_store.py` (6 Szenarien)
6. Metamorphic Tests in `test_metamorphic_certificate_store.py` (2 Properties)
7. CHANGELOG.md Eintrag

**Warum:** Experiment #80 zeigte 70% Mean Reduction durch Z3-Konsistenzfilter
und perfekte Erkennung kontradiktiver Praemissen.

**Kernlogik:** Praemissen + Conclusion jedes Zertifikats als Z3-Konjunktion pruefen.
SAT = konsistent (behalten), UNSAT = inkonsistent (ausfiltern). Kontradiktive
Praemissen vorab erkennen.

**Dateien die du lesen musst:**

| Datei | Warum |
|-------|-------|
| `logic_brain/certificate_store.py` | Inklusive compact() aus #81 |
| `logic_brain/parser.py` | `parse_expression()` fuer Praemissen-Parsing |
| `tests/experiments/test_context_retrieval.py` | Experiment-Code als Referenz |
| Gleiche Dateien wie #81 | Tests, STABILITY.md, CHANGELOG.md |

---

## Wichtige Dateien zum Lesen vor dem Start

| Datei | Warum |
|-------|-------|
| `docs/agent_collaboration.md` | Vollstaendige Rollendefinition |
| `docs/development_process.md` | Kanonischer Workflow |
| `logic_brain/certificate_store.py` | Primaere Datei fuer beide Issues |
| `logic_brain/certificate.py` | ProofCertificate, PROPOSITIONAL_CLAIM |
| `logic_brain/parser.py` | parse_argument(), parse_expression() |
| `logic_brain/verifier.py` | PropositionalVerifier._to_z3() |
| `STABILITY.md` | Tier-2-Tabelle |

---

## Eskalationsprotokoll

Wenn du auf eine Situation triffst, die im Issue nicht vorgesehen ist:

1. **Nicht selbst entscheiden** — kein Scope hinzufuegen
2. **Issue kommentieren** mit genauer Beschreibung der Unklarheit
3. **Warten auf Antwort vom Head-Agent** (Claude)

Typische Eskalationsgruende:
- "PropositionalVerifier._to_z3() ist private — soll ich direkt z3 nutzen stattdessen?"
- "mypy beschwert sich ueber den Typ von certificate.claim (str | dict)"
- "Circular import zwischen certificate_store.py und parser.py"

---

## Was du auf keinen Fall tun darfst

- Bestehende Tier-1-APIs veraendern (definiert in `STABILITY.md`)
- Issues oeffnen (das ist Claude's Aufgabe)
- Commits ohne gruene Preflight Gates pushen
- Scope eigenstaendig erweitern ("das mache ich gleich mit")
- `--no-verify`, force-push, Rebase von shared history
- MCP-Tools aendern (kommt in einem spaeteren Issue, falls gewuenscht)

---

## Abschluss eines Issues

Nach erfolgreichem Commit:

```bash
gh issue close 81 --comment "Implemented in commit $(git rev-parse --short HEAD). All preflight gates green."
```

Dann: naechstes Issue lesen und starten.
