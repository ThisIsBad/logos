# Vision & Roadmap: LogicBrain als deterministischer Zustandsmanager

## Kernprinzip

**LLMs sind probabilistische Token-Generatoren. Sie brauchen deterministische Leitplanken, um zuverlässig zu sein.**

LogicBrain liefert diese Leitplanken: Z3 und Lean 4 als unbestechliche Richter, die mit 100% Sicherheit sagen können, ob ein logischer Schritt korrekt ist.

## Architektur-Entscheidung: Hybrid-Ansatz

Nach Analyse der Optionen haben wir uns für einen **Hybrid-Ansatz** entschieden:

| Komponente | Verantwortung |
|------------|---------------|
| **Agent** (Claude Code, etc.) | Probabilistische Entscheidungen: Welche Taktik? Backtracking? Strategie? |
| **LogicBrain** | Deterministische Garantien: Verifikation, Zustandsverwaltung, REPL-Interface |

### Warum nicht Loop in LogicBrain?

- Dupliziert was Agenten bereits können (LLM-Calls, Retry-Logik)
- Weniger flexibel (festgelegte Strategie)
- Eigene API-Key-Verwaltung nötig

### Warum nicht nur Agent?

- Agent kann Lean/Z3-Output nicht zuverlässig parsen
- Zustandsverwaltung über langen Kontext ist fehleranfällig
- Kein Mehrwert durch LogicBrain

### Der Hybrid-Sweet-Spot

LogicBrain wird zum **"Smart Tool"** - es verwaltet den deterministischen Zustand, der Agent trifft die Entscheidungen.

```
Agent
    └── ruft LogicBrain.LeanSession() auf
        ├── session.apply("tactic1") → Goal State
        ├── session.apply("tactic2") → Goal State  
        └── Agent entscheidet, LogicBrain führt aus
```

---

## Das Kernproblem: One-Shot vs. Iterativ

### Status Quo (One-Shot)

```
[LLM generiert 20 Schritte] → [Verifier: "Schritt 3 war falsch"]
                              → 17 Schritte verschwendet, alles neu
```

Das LLM halluziniert nach dem ersten Fehler weiter, baut auf falschen Annahmen auf.

### Ziel (Iterativ mit REPL)

```
[LLM: Schritt 1] → [Verifier: OK] → weiter
[LLM: Schritt 2] → [Verifier: OK] → weiter
[LLM: Schritt 3] → [Verifier: FAIL] → sofort korrigieren
```

Fehler werden sofort erkannt. Kein Aufbauen auf falschen Annahmen.

---

## Implementierte Komponenten (aktueller Stand)

Die folgenden Kernkomponenten sind implementiert und getestet (333 Tests, 90.33% Coverage, 47 Metamorphic-Tests):

### Lean REPL-Wrapper (`lean_session.py`)

Interaktive Lean 4 Sessions, die der Agent Taktik-für-Taktik steuern kann.

```python
from logic_brain import LeanSession

session = LeanSession()
session.start("theorem test : 1 + 1 = 2 := by")
result = session.apply("rfl")
print(session.is_complete)  # True
```

### Z3 Incremental Solving (`z3_session.py`)

Stateful Z3 Sessions mit push/pop, unsat-core und sicherem AST-basiertem Constraint-Parsing.

```python
from logic_brain import Z3Session

session = Z3Session()
session.declare("x", "Int")
session.assert_constraint("x > 0")
print(session.check())  # sat
```

### Strukturierte Diagnostik (`diagnostics.py`)

Maschinenlesbare Fehlerklassifikation mit Vorschlägen für Agent-Recovery.

```python
result = session.apply("apply Nat.add_comm")
if not result.success:
    print(result.error_type)   # "tactic_failed"
    print(result.suggestion)   # "Did you mean: apply Nat.mul_comm?"
```

### Propositional & Predicate Logic Verifier

Quick-Verify API und vollständiger FOL-Verifier mit Z3-Backend.

```python
from logic_brain import verify
result = verify("P -> Q, P |- Q")
print(result.valid, result.rule)  # True, "Modus Ponens"
```

### Frische Problemgenerierung fuer Agent-Evaluation (`generator.py`)

`ProblemGenerator` ist aus der Public API exportiert (Tier 2 / Provisional)
und erzeugt reproduzierbare, zur Laufzeit neue Aufgaben.

```python
from logic_brain import ProblemGenerator

gen = ProblemGenerator()
problems = gen.generate_batch(3)
print(problems[0]["ground_truth_valid"])
```

### Erweiterte deterministische Reasoning-Module

- `certificate.py`: Proof-Carrying Zertifikate fuer Verifier- und Z3-Ergebnisse
- `assumptions.py`: typisierte Annahmen mit Lifecycle und Konsistenz-Schnittstellen
- `counterfactual.py`: deterministische Branch-Planung ueber `Z3Session`
- `action_policy.py`: harte Pre-Action-Policies mit strukturierten Violations
- `uncertainty.py`: Confidence-Kalibrierung und Eskalationsregeln
- `proof_exchange.py`: transport-sichere Proof-Bundles fuer Zero-Trust-Austausch
- `belief_graph.py`: kausaler/temporaler Belief-Graph mit Widerspruchserklaerungen
- `goal_contract.py`: Goal Contracts mit deterministischer Auswertung und Z3-Precondition-Checks

### Support- und Infrastrukturmodule

- `parser.py`, `models.py`, `verifier.py`, `predicate.py`, `predicate_models.py`: Kernlogik fuer propositionalen und praedikatenlogischen Verify-Flow
- `cli.py`, `__main__.py`: CLI-Einstiegspunkte fuer direkte Nutzung
- `lean_verifier.py`: nicht-interaktive Lean-Verifikation als Ergaenzung zu `LeanSession`
- `analyzer.py`, `loader.py`, `runner.py`, `external.py`, `evaluate.py`: Benchmark-, Analyse- und Auswertungs-Tooling
- `schema_utils.py`: gemeinsame Schema-/JSON-Helfer fuer die neueren Datentransportmodule
- `__init__.py`: stabiler Public-API-Reexport ueber Tier-1- und Tier-2-Symbole

### CI & Tooling

- GitHub Actions CI (Python 3.10/3.11/3.12)
- Ruff-Linting als Gate
- mypy strict als Gate
- Coverage-Gate (>=85%) + Coverage-Artefakt
- Explizites Metamorphic-Test-Gate (`pytest -m metamorphic`)
- Benchmark-Regression-Gate (`tools/check_results.py exam`)
- Konsolidierte Benchmark-Tools unter `tools/`
- Release-Playbook unter `docs/release_playbook.md`

### Metamorphic Quality Layer

Mit `docs/metamorphic_ledger.md` ist ein versionierter MR-Katalog eingefuehrt,
der relationale Invarianten fuer Verifier, Parser und Z3Session als
"Super-Axiome" dokumentiert und direkt auf konkrete Tests referenziert.

### Formale Grenzen und Z3-Erdung

Die formalen Garantien sind jetzt explizit in `docs/formal_guarantees.md`
dokumentiert. Wichtig ist die Trennung zwischen:

- **Z3-geerdeten Garantien** fuer `verifier`, `predicate`, `z3_session` sowie die bereits angebundenen Teile von `assumptions`, `belief_graph` und `goal_contract`
- **strukturellen Garantien** fuer Module, die deterministisch und serialisierbar sind, aber noch keine vollstaendige formale Absicherung ueber Z3 haben

---

## Nicht in Scope (Agent-Verantwortung)

Diese Dinge macht der Agent, nicht LogicBrain:

- **MCTS / Baumsuche** - Agent entscheidet Exploration vs. Exploitation
- **Retry-Logik** - Agent entscheidet wann und wie oft
- **LLM-Calls** - Agent hat eigene API-Anbindung
- **Strategie-Auswahl** - Agent wählt Ansatz (Induktion, Fallunterscheidung, etc.)

LogicBrain ist das **Werkzeug**, nicht der **Arbeiter**.

---

## Zusammenfassung

```
┌─────────────────────────────────────────────────────────────┐
│  Agent (Claude Code / OpenCode / Aider)                     │
│  - Probabilistisch                                          │
│  - Entscheidet: Was tun?                                    │
│  - Strategie, Backtracking, Retry                           │
└────────────────────────┬────────────────────────────────────┘
                         │ session.apply("tactic")
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  LogicBrain (REPL-Wrapper)                                  │
│  - Deterministisch                                          │
│  - Garantiert: Schritt korrekt oder nicht                   │
│  - Zustand, Goals, Fehlerdiagnose                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Lean 4 / Z3                                                │
│  - Mathematisch korrekt                                     │
│  - Keine Kompromisse                                        │
└─────────────────────────────────────────────────────────────┘
```

**Das Prinzip:** LLM generiert (probabilistisch), Verifier prüft (deterministisch). LogicBrain macht die Schnittstelle zwischen beiden so nutzbar wie möglich.

---

## Roadmap-Status

### Abgeschlossen: v0.1.3 -> v0.2.0

**→ [`docs/roadmap_v013_v020.md`](docs/roadmap_v013_v020.md)**

1. **v0.1.3 — API Stabilization**: Stabilitätsvertrag, Deprecation-Policy, interne API-Grenzen, Root-Cleanup
2. **v0.1.4 — Quality & Observability**: neue Test-Suites, Ruff + CI-Haertung, Benchmark-Regression-Gate
3. **v0.2.0 — Integration & Documentation**: Agent-Integrationsbeispiel, API-Referenz, PEP-561 Marker, erweitertes Public API

Post-v0.2.0 Quality Gates (Issues #21–#28, alle CLOSED):
- Coverage-Gate (85%), mypy strict Gate, 333 Tests, 90.33% Coverage
- Metamorphic Testing Layer (47 MR-Tests, Ledger, CI-Gate)
- Development Process Hardening (Issue-first, Dogfooding)

### Implementiert nach v0.2.0

**→ [`docs/roadmap_v030_v070.md`](docs/roadmap_v030_v070.md), [`docs/roadmap_v080_v120.md`](docs/roadmap_v080_v120.md)**

Tatsaechlich umgesetzt wurde kein linearer Ausbau entlang der alten "Aktiv"-Liste,
sondern ein Sprung zu mehreren spaeteren Infrastrukturbausteinen. Der reale Stand:

1. **v0.3 — Proof-Carrying Actions**: implementiert als `certificate.py`
2. **v0.8 — Assumption & World-State Kernel**: implementiert als `assumptions.py`; Z3-Erdung fuer Konsistenzpruefung inzwischen angebunden
3. **v0.9 — Counterfactual Planner**: implementiert als `counterfactual.py`
4. **v1.0 — Verified Action Policies**: initial implementiert als `action_policy.py`; aktuell deterministisch, aber noch nicht vollstaendig Z3-geerdet
5. **v1.1 — Uncertainty Calibration Layer**: implementiert als `uncertainty.py`
6. **v1.2 — Composed Proof Exchange**: implementiert als `proof_exchange.py`
7. **v1.3 — Belief Graph**: implementiert als `belief_graph.py`; Widerspruchsarbeit inzwischen teilweise Z3-geerdet
8. **v1.4 — Goal Contracts**: implementiert als `goal_contract.py`; Precondition-Verifikation inzwischen Z3-angebunden

### Superseded oder anders realisiert

- **v0.4 — Reasoning Contracts**: nicht als eigenes Modul gebaut; funktional spaeter in `goal_contract.py` aufgegangen
- **v0.5 — Self-Consistency Checker**: nicht als separates Artefakt gebaut; Teile davon leben heute in `assumptions.py` und `belief_graph.py`
- **v0.6 — Policy-Guided Search**: nur teilweise realisiert; `action_policy.py` existiert, voll formale Policy-Konsistenz steht noch aus
- **v0.7 — Compositional Proof Orchestrator**: nicht als eigener Orchestrator gebaut; `proof_exchange.py` deckt den Austausch-Layer ab

### Weiterhin geplant / noch nicht finalisiert

Die spaeteren Module existieren bereits, aber teilweise noch als erste
Implementierungen. Insbesondere bei `action_policy.py` ist die vollstaendige
Z3-Erdung noch offen; die Unterschiede zwischen formalen und strukturellen
Garantien sind in `docs/formal_guarantees.md` festgehalten.

### Bewusst zurückgestellt

- Logik-Erweiterungen (Modal/Temporal/Many-valued) — orthogonal zur Agent-Tooling-Roadmap, siehe `docs/logic_extensions_assessment.md`
- Lemma-Cache — erst bei nachgewiesener Agent-Nutzung von LeanSession
- PyPI-Release — erst nach stabilem API-Vertrag

---

## Referenzen

- Roadmap v0.3–v0.7: `docs/roadmap_v030_v070.md`
- Roadmap v0.8–v1.2: `docs/roadmap_v080_v120.md`
- Roadmap v0.1.3–v0.2.0 (abgeschlossen): `docs/roadmap_v013_v020.md`
- Formale Garantien und Grenzen: `docs/formal_guarantees.md`
- Metamorphic Ledger: `docs/metamorphic_ledger.md`
- Planning Brief: `docs/claude_opus_planning_brief.md`
- Extensions Assessment: `docs/logic_extensions_assessment.md`
- Release Playbook: `docs/release_playbook.md`
- Development Process: `docs/development_process.md`
- Changelog: `CHANGELOG.md`
