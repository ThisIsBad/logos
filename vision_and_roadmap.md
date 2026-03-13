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

## Implementierte Komponenten (v0.1.2)

Die folgenden Kernkomponenten sind implementiert und getestet (153 Tests):

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

### CI & Tooling

- GitHub Actions CI (Python 3.10/3.11)
- Konsolidierte Benchmark-Tools unter `tools/`
- Release-Playbook unter `docs/release_playbook.md`

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

## Aktuelle Roadmap (ab v0.1.3)

Die detaillierte Roadmap mit Phasen, KPIs, Issue-Vorschlägen und Risikoanalyse liegt in:

**→ [`docs/roadmap_v013_v020.md`](docs/roadmap_v013_v020.md)**

Zusammenfassung der drei Phasen:

1. **v0.1.3 — API Stabilization** (2-3 Wochen): Stabilitätsvertrag, Deprecation-Policy, interne API-Grenzen, Root-Cleanup
2. **v0.1.4 — Quality & Observability** (2-3 Wochen): Test-Coverage ≥85%, CI mit Linting/mypy/Coverage, Benchmark-Regression-Gate
3. **v0.2.0 — Integration & Documentation** (3-4 Wochen): Agent-Integrationsbeispiel, API-Referenz, erstes "stable" Release

### Bewusst zurückgestellt

- Logik-Erweiterungen (Modal/Temporal/Many-valued) — erst nach v0.2.0, siehe `docs/logic_extensions_assessment.md`
- Lemma-Cache — erst bei nachgewiesener Agent-Nutzung von LeanSession
- PyPI-Release — erst nach stabilem API-Vertrag

---

## Referenzen

- Detaillierte Roadmap: `docs/roadmap_v013_v020.md`
- Planning Brief: `docs/claude_opus_planning_brief.md`
- Extensions Assessment: `docs/logic_extensions_assessment.md`
- Release Playbook: `docs/release_playbook.md`
- Changelog: `CHANGELOG.md`
