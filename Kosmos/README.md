# Kosmos

**AGI Stage:** 3–4 | **Phase:** 2 | **Status:** 🔲 Not implemented

Kausales Reasoning mit Do-Calculus — Welt-Modellierung jenseits von Korrelationen.
Schließt die Lücke: *"Transformers learn distributional correlations, not causal structure. Interventional reasoning requires explicit causal graphs."*

## Motivation

LLMs lernen statistische Muster, keine Kausalstrukturen. "Was passiert, wenn
ich X tue?" erfordert interventionales Denken (Pearl's Do-Calculus), nicht
nur Mustererkennung. Kosmos speichert und verwaltet kausale Graphen.

## Pearl's 3 Ebenen der Kausalität

```
Ebene 1: Assoziation       P(Y | X)          "Was beobachte ich?"
Ebene 2: Intervention      P(Y | do(X))       "Was passiert, wenn ich X tue?"
Ebene 3: Kontrafaktisch    P(Y_x | X', Y')    "Was wäre passiert, wenn...?"
```

Kosmos unterstützt alle 3 Ebenen. Ebene 3 delegiert an Logos `counterfactual_branch`.

## MCP-Tools

| Tool | Beschreibung |
|------|-------------|
| `add_causal_edge` | Fügt eine Kausal-Beziehung zum Graphen hinzu |
| `compute_intervention` | Berechnet Downstream-Effekte einer Aktion (do(X)) |
| `counterfactual` | Was wäre anders gewesen, wenn...? (Ebene 3) |
| `query_causes` | Gibt die Kausal-Kette für einen Effekt zurück |
| `get_causal_graph` | Snapshot des gesamten oder domänen-spezifischen Graphen |

## Knoten-Typen im Kausal-Graphen

- `variable` — beobachtbare Größe
- `action` — ausführbare Intervention
- `outcome` — Ergebnis/Konsequenz
- `context` — Rahmenbedingung (moderiert andere Kanten)

## Tech Stack

- Python 3.12
- FastAPI + MCP HTTP transport
- NetworkX (gerichteter azyklischer Graph)
- pgmpy (probabilistische Graphische Modelle, Do-Calculus)
- Logos-Client (Kontrafaktische Verifikation)

## Deployment (Railway)

```
web: python -m world_model.mcp_server_http
```

## Referenzen

- Pearl: Causality (2000), The Book of Why (2018)
- Schölkopf et al. (2021) — Toward Causal Representation Learning
- `../Logos/` — counterfactual_branch Tool
- `../ROADMAP.md §4` — Vollständige Spec
