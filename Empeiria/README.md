# Empeiria

**AGI Stage:** 4 | **Phase:** 3 | **Status:** 🔲 Not implemented

Erfahrungs-Akkumulation und Muster-Extraktion über Sessionen hinweg.
Schließt die Lücke: *"Post-deployment improvement requires an exploration–exploitation loop, not just inference."*

## Motivation

Ohne Empeiria beginnt jeder Task bei Null. Mit Empeiria akkumuliert
der Agent Wissen darüber, welche Strategien für welche Aufgaben funktioniert
haben — und wird über Zeit besser, ohne Retraining.

## MCP-Tools

| Tool | Beschreibung |
|------|-------------|
| `record_experience` | Speichert Aktion + Outcome + Kontext |
| `retrieve_lessons` | Ähnliche vergangene Erfahrungen + extrahierte Lektionen |
| `extract_patterns` | Wiederkehrende Erfolgs- und Fehlermuster identifizieren |
| `get_skill_candidates` | Erfahrungen die reif für Techne-Promotion sind |

## Erfahrungs-Schema

```json
{
  "task": "Implement a binary search tree in Python",
  "action": "Used recursive approach with height balancing",
  "outcome": "Tests passed, but performance was suboptimal for large inputs",
  "success": false,
  "lesson": "For large inputs, iterative AVL tree is preferable",
  "domain": "coding",
  "timestamp": "2026-04-13T17:00:00Z"
}
```

## Promotion-Pipeline

```
Empeiria.record_experience()
    → extract_patterns() identifiziert bewährte Strategie
    → get_skill_candidates() schlägt Promotion vor
    → Techne.promote_experience() speichert als Skill
    → (optional) Logos.certify_claim() verifiziert den Skill
```

## Stage 4 Acceptance Criterion

Cross-task improvement: ≥ 15% bessere Performance vs. Cold Start auf verwandten Tasks (GAIA Level 2+)

## Tech Stack

- Python 3.12
- FastAPI + MCP HTTP transport
- SQLite (strukturierte Erfahrungen)
- ChromaDB (semantische Ähnlichkeitssuche für `retrieve_lessons`)

## Deployment (Railway)

```
web: python -m experience_bus.mcp_server_http
```

## Referenzen

- Reflexion: Shinn et al. (2023) — Language Agents with Verbal Reinforcement
- GFlowNets: Bengio et al. (2021) — Generative Flow Networks
- GAIA Benchmark: Mialon et al. (2023)
- `../Techne/` — Promotion-Ziel
- `../ROADMAP.md §4` — Vollständige Spec
