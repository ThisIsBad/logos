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

## Roadmap

### Phase 1: Lean REPL-Wrapper (ERLEDIGT)

**Status:** Implementiert in `logic_brain/lean_session.py` mit 18 Tests.

### Phase 1 (Original):

**Ziel:** Interaktive Lean 4 Sessions, die der Agent Taktik-für-Taktik steuern kann.

```python
from logic_brain import LeanSession

session = LeanSession()
session.start("theorem test : 1 + 1 = 2 := by")

print(session.goals)       # ["⊢ 1 + 1 = 2"]
print(session.is_complete) # False

result = session.apply("rfl")
print(result.success)      # True
print(session.goals)       # []
print(session.is_complete) # True
print(session.proof)       # "theorem test : 1 + 1 = 2 := by rfl"
```

**Was LogicBrain liefert:**
- Zustandsverwaltung (offene Goals, bisherige Taktiken)
- Goal-State-Parsing (Lean-Output → strukturierte Daten)
- Fehlerbehandlung (Timeout, Syntax-Fehler, etc.)

**Was der Agent macht:**
- Taktik-Auswahl ("Welchen Schritt probiere ich?")
- Backtracking ("Sackgasse, zurück zu Schritt 3")
- Strategie ("Erst vereinfachen, dann induktiv")

**Aufwand:** 2-3 Tage

### Phase 2: Z3 Incremental Solving (ERLEDIGT)

**Status:** Implementiert in `logic_brain/z3_session.py` mit 31 Tests.

### Phase 2 (Original):

Ähnlich wie Lean-REPL, aber für Z3:

```python
from logic_brain import Z3Session

session = Z3Session()
session.declare("x", "Int")
session.declare("y", "Int")

session.assert_constraint("x > 0")
print(session.check())  # sat

session.assert_constraint("x < 0")
print(session.check())  # unsat
print(session.unsat_core())  # ["x > 0", "x < 0"]
```

**Aufwand:** 1-2 Tage (Z3 hat gute Python-Bindings)

### Phase 3: Strukturierte Diagnostik (ERLEDIGT)

**Status:** Implementiert in `logic_brain/diagnostics.py` und in Lean/Z3 integriert.

Bessere Fehlerausgaben, die der Agent direkt nutzen kann:

```python
result = session.apply("apply Nat.add_comm")
if not result.success:
    print(result.error_type)     # "tactic_failed"
    print(result.expected_type)  # "⊢ a + b = b + a"
    print(result.actual_type)    # "⊢ a * b = b * a"
    print(result.suggestion)     # "Did you mean: apply Nat.mul_comm?"
```

**Ergebnis:**
- `TacticResult` und `CheckResult` liefern strukturierte Diagnostik
- Fehlerklassifikation (`ErrorType`) + Vorschläge (`suggestions`)
- Neue Tests für Diagnostikpfade vorhanden

### Phase 4: Lemma-Cache (Priorität: NIEDRIG)

Erfolgreiche Zwischen-Lemmata speichern und wiederverwenden:

```python
# Automatisch nach erfolgreichem Beweis
session.save_lemma("my_helper", "∀ n, n + 0 = n")

# Später in anderem Beweis
session.use_lemma("my_helper")
```

**Aufwand:** 1-2 Wochen

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

## Nächste Schritte (ab v0.1.1)

1. **CI stabilisieren**
   - GitHub Actions Workflow für `pip install -e ".[dev]"` + `pytest -q`
   - Python-Versionen 3.10/3.11 abdecken

2. **Tooling vereinheitlichen**
   - Restliche Check-Skripte (`check_lean.py`, `check_predicate.py`) unter `tools/` konsolidieren
   - Einheitliche CLI-Parameter und Doku

3. **Optionale Erweiterungen planen**
   - Konkrete Umsetzung nach `docs/logic_extensions_assessment.md`
   - Empfohlene Reihenfolge: Modal -> Temporal -> Many-valued

---

## Session-Handoff (2026-03-12)

- Release `v0.1.1` ist live.
- Tests: `144 passed`.
- Roadmap-Issues `#1` bis `#5` geschlossen.
- Fokus für Folgesession: CI + Tooling-Konsolidierung.
