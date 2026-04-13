# PlannerBrain

**AGI Stage:** 3 | **Phase:** 1 | **Status:** 🔲 Not implemented

Hierarchisches Planning mit State-Space-Search und Backtracking.
Schließt die Lücke: *"LLMs generate plans autoregressively — they don't search a state space or backtrack."*

## Motivation

LLMs generieren Pläne in einem Durchgang — ohne Zustandsraum-Suche, ohne
systematisches Backtracking bei Fehlern. PlannerBrain implementiert echtes
hierarchisches Planning mit Verifikation via LogicBrain.

## MCP-Tools

| Tool | Beschreibung |
|------|-------------|
| `decompose_goal` | Zerlegt ein Ziel rekursiv in Sub-Goals und Steps |
| `evaluate_step` | Bewertet Machbarkeit und Risiken eines Schritts |
| `backtrack` | Findet alternative Pfade nach einem fehlgeschlagenen Schritt |
| `verify_plan` | Validiert einen Plan via LogicBrain GoalContract |
| `commit_step` | Markiert einen Schritt als ausgeführt + speichert Outcome |
| `get_plan` | Gibt den aktuellen Plan-Zustand zurück |

## Architektur

```
PlannerBrain
├── GoalDecomposer    → Goal → Sub-Goals → Steps (NetworkX Tree)
├── StepEvaluator     → Feasibility, Confidence, Risk-Scoring
├── TreeSearch        → BFS/DFS mit Kosten-Pruning (Tree of Thoughts)
├── BacktrackEngine   → Alternative Branches bei Failure
├── PlanVerifier      → LogicBrain GoalContract Integration
└── PlanHistory       → SQLite: ausgeführte Pläne + Outcomes
```

## Plan-Zustände

```
Goal
└── SubGoal 1
    ├── Step 1.1  [pending / in_progress / done / failed]
    ├── Step 1.2
    └── Step 1.3
└── SubGoal 2
    └── ...
```

## Tech Stack

- Python 3.12
- FastAPI + MCP HTTP transport
- NetworkX (Baum- und Graphstruktur)
- SQLite (Plan-History)
- LogicBrain-Client (Plan-Verifikation)

## Deployment (Railway)

```
web: python -m planner_brain.mcp_server_http
```

## Referenzen

- Tree of Thoughts: Yao et al. (2023)
- RAP: Hao et al. (2023) — Reasoning via Planning
- LATS: Zhou et al. (2023) — Language Agent Tree Search
- `../ROADMAP.md §4` — Vollständige Spec
