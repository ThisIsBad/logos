# SelfModel

**AGI Stage:** 3 | **Phase:** 2 | **Status:** 🔲 Not implemented

Metakognition und Kalibrierung — der Agent modelliert seine eigene Kompetenz.
Schließt die Lücke: *"LLMs cannot reliably estimate their own uncertainty. Calibration remains an open problem."*

## Motivation

Ein AGI-fähiger Agent muss wissen, *wann* er sich irren könnte. SelfModel
verfolgt Konfidenz vs. tatsächliche Korrektheit über Zeit und berechnet den
Expected Calibration Error (ECE) pro Domäne. Stage 3 Acceptance Criterion: ECE ≤ 0.10.

## MCP-Tools

| Tool | Beschreibung |
|------|-------------|
| `log_prediction` | Speichert eine Vorhersage mit Konfidenzwert und Domäne |
| `log_outcome` | Speichert das tatsächliche Ergebnis zu einer Vorhersage |
| `get_calibration` | ECE, Bias und Sharpness für eine Domäne oder gesamt |
| `should_escalate` | Entscheidet ob eine Behauptung eskaliert werden soll |
| `get_competence_map` | Zeigt systematische Stärken/Schwächen pro Domäne |

## Kalibrierungs-Metriken

- **ECE (Expected Calibration Error):** Abweichung zwischen Konfidenz und Accuracy
- **Bias:** Systematische Über- oder Unter-Konfidenz
- **Sharpness:** Wie entschlossen sind die Vorhersagen?

Ziel: ECE ≤ 0.10 über 200 diverse Claims (Stage 3 Acceptance Criterion)

## Domänen (initial)

`coding`, `mathematics`, `factual`, `reasoning`, `planning`, `general`

## Tech Stack

- Python 3.12
- FastAPI + MCP HTTP transport
- SQLite (Prediction Log)
- scipy (ECE-Berechnung, Kalibrierungs-Analyse)

## Deployment (Railway)

```
web: python -m self_model.mcp_server_http
```

## Referenzen

- Kadavath et al. (2022) — Language Models (Mostly) Know What They Know
- Lin et al. (2022) — Teaching Models to Express Their Uncertainty
- `../ROADMAP.md §4` — Vollständige Spec
