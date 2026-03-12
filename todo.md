# LogicBrain - Roadmap & TODOs

## Status Quo

Das Projekt hat einen funktionierenden Z3-basierten Verifier. 

**Erkenntnis:** Weder ein eigener "Core Loop" noch ein MCP-Server sind nötig. Agentic Tools (Claude Code, OpenCode, etc.) können den Verifier **direkt via Python-Ausführung** nutzen.

```
Test 1 - Modus Ponens: valid=True, rule=Modus Ponens
Test 2 - Affirming Consequent: valid=False, rule=Affirming the Consequent (fallacy)
   Counterexample: {'P': False, 'Q': True}
Test 3 - Hypothetical Syllogism: valid=True, rule=Hypothetical Syllogism
```

---

## Was LogicBrain IST

Ein **Z3-backed Logic Verifier** als Python-Library. Fertig.

- Agenten schreiben Python-Code
- Agenten führen ihn aus
- Agenten lesen das Ergebnis
- Agenten korrigieren sich selbst

Kein Wrapper, kein Server, kein Overhead nötig.

---

## Phase 1: Developer Experience verbessern (Priorität: HOCH)

### 1.1 String-Parser für schnelle Nutzung
- [ ] `logic_brain/parser.py` erstellen
- [ ] Einfache Syntax: `verify("P -> Q, P |- Q")`
- [ ] Unterstützte Notationen:
  ```
  P -> Q      (Implikation)
  P & Q       (Konjunktion)  
  P | Q       (Disjunktion)
  ~P oder !P  (Negation)
  P <-> Q     (Bikonditional)
  |-          (Konklusion)
  ```
- [ ] Beispiel:
  ```python
  from logic_brain import quick_verify
  result = quick_verify("P -> Q, P |- Q")
  # => valid=True, rule="Modus Ponens"
  ```

### 1.2 CLI für Standalone-Nutzung
- [ ] `python -m logic_brain "P -> Q, P |- Q"`
- [ ] JSON-Output-Option: `--json`
- [ ] Verbose-Mode: `--explain`

---

## Phase 2: Codequalität (Priorität: MITTEL)

### 2.1 Type Hints fixen
- [ ] Z3-Types sind problematisch (Pyright-Errors)
- [ ] `# type: ignore` wo nötig, oder Casts
- [ ] `py.typed` Marker hinzufügen

### 2.2 Tests erweitern
- [ ] Property-based testing mit Hypothesis
- [ ] Fuzzing: Zufällige Formeln generieren und Verifier prüfen
- [ ] Edge Cases: Leere Prämissen, sehr tiefe Verschachtelung

### 2.3 Cleanup
- [ ] `check_*.py` Scripts konsolidieren oder entfernen
- [ ] `test_direct.py` entfernen (war nur Beweis)
- [ ] Unbenutzte Imports entfernen

---

## Phase 3: Dokumentation (Priorität: MITTEL)

### 3.1 README erweitern
- [ ] Klare Positionierung: "Library für Agenten, kein eigenständiges Tool"
- [ ] Beispiele für Claude Code / OpenCode Integration
- [ ] API-Referenz

### 3.2 Beispiele
- [ ] `examples/` Ordner mit Anwendungsfällen
- [ ] Jupyter Notebook für interaktive Demos

---

## Phase 4: Optionale Erweiterungen (Priorität: NIEDRIG)

### 4.1 Mehr Logik-Systeme
- [ ] Modale Logik (Box, Diamond)
- [ ] Temporale Logik (LTL, CTL)
- [ ] Mehrwertige Logik

### 4.2 Lean 4 verbessern
- [ ] Bessere Fehlerextraktion
- [ ] Mathlib-Integration testen

---

## Nicht nötig (gestrichen)

- ~~MCP-Server~~ - Direkte Python-Ausführung reicht
- ~~Core Loop~~ - Agenten machen das
- ~~LLM-Client~~ - Agenten machen das
- ~~Retry-Logik~~ - Agenten machen das
- ~~Prompt-Engineering~~ - Agenten machen das

---

## Quick Wins

1. **[x] ~~String-Parser~~** - `verify("P -> Q, P |- Q")` implementiert!
2. **[x] ~~Beweis dass es funktioniert~~** - `test_direct.py` zeigt es
3. **[x] ~~Type Hints fixen~~** - Z3-Errors mit `# type: ignore` gelöst
4. **[x] ~~README aktualisieren~~** - Neue API dokumentiert, Architektur-Diagramm entfernt

---

## Architektur-Fazit

```
┌─────────────────────────────────────────────────┐
│  Claude Code / OpenCode / Aider                 │
│  (Agent mit Bash-Tool)                          │
└────────────────────┬────────────────────────────┘
                     │ python test.py
                     ▼
┌─────────────────────────────────────────────────┐
│  LogicBrain (Python Library)                    │
│  - PropositionalVerifier                        │
│  - PredicateVerifier                            │
│  - LeanVerifier                                 │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│  Z3 SMT Solver                                  │
└─────────────────────────────────────────────────┘
```

**Das ist alles. Kein MCP. Kein Loop. Einfach eine Library.**

---

*Erstellt: 2026-03-12*  
*Letzte Aktualisierung: 2026-03-12*
