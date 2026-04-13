# DriftGuard

**AGI Stage:** 4 | **Phase:** 3 | **Status:** 🔲 Not implemented

Ziel-Stabilitäts-Monitor gegen Goal Drift und Mesa-Optimization.
Schließt die Lücke: *"Without explicit goal representation, systems drift with each prompt turn."*

## Motivation

Über lange Horizonte können Agenten ihr ursprüngliches Ziel aus den Augen
verlieren — durch Prompt-Drift, Kontext-Fenster-Grenzen oder subtile
Zielverlagerung (Mesa-Optimization, Hubinger et al. 2019). DriftGuard
registriert Ziele formal und überwacht jede Aktion dagegen.

Enge Integration mit LogicBrain `GoalContract`: Ziel-Constraints werden
als formale Verifikations-Aufgaben hinterlegt.

## MCP-Tools

| Tool | Beschreibung |
|------|-------------|
| `register_goal` | Registriert ein Ziel mit Constraints (→ LogicBrain GoalContract) |
| `check_action_alignment` | Prüft ob eine Aktion mit dem registrierten Ziel übereinstimmt |
| `get_drift_history` | Zeigt Drift-Score-Verlauf für ein Ziel über Zeit |
| `alert_misalignment` | Löst Alert aus bei erkannter Ziel-Abweichung |
| `list_active_goals` | Gibt alle aktiven Ziele zurück |

## Drift-Score

Der Drift-Score (0.0–1.0) misst wie stark das beobachtete Verhalten vom
registrierten Ziel abweicht:

```
0.0  →  perfekt aligned
0.5  →  neutral / unklar
1.0  →  vollständige Abweichung → Alert
```

## Stage 4 Acceptance Criterion

Goal stability: Drift ≤ 5% über einen Horizont von 1000 Aktionen.

## Integration mit LogicBrain

```python
# Ziel registrieren → LogicBrain GoalContract erstellen
register_goal(
    description="Implement feature X without breaking existing tests",
    constraints=["no_test_deletion", "no_scope_expansion"]
)
# → intern: LogicBrain.check_contract(goal_constraints)
```

## Tech Stack

- Python 3.12
- FastAPI + MCP HTTP transport
- SQLite (Goal Registry, Drift History, Alert Log)
- LogicBrain-Client (GoalContract-Integration, formale Constraint-Prüfung)

## Deployment (Railway)

```
web: python -m drift_guard.mcp_server_http
```

## Referenzen

- Omohundro (2008) — The Basic AI Drives
- Hubinger et al. (2019) — Risks from Learned Optimization (Mesa-Optimization)
- `../LogicBrain/` — GoalContract, check_contract Tool
- `../ROADMAP.md §4` — Vollständige Spec
