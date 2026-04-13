# SkillLibrary

**AGI Stage:** 4 | **Phase:** 3 | **Status:** 🔲 Not implemented

Persistente, verifizierte Skill-Bibliothek für AI-Agenten.
Schließt die Lücke: *"LLMs cannot accumulate and reuse verified strategies across sessions."*

## Motivation

Inspiriert von **Voyager** (Wang et al., 2023): Der Minecraft-Agent der dauerhaft
Skills aufbaut und wiederverwendet. SkillLibrary überträgt dieses Konzept auf
allgemeine AI-Agenten — mit dem Unterschied, dass Skills via LogicBrain
verifiziert werden können (`verified=True`).

## MCP-Tools

| Tool | Beschreibung |
|------|-------------|
| `store_skill` | Speichert einen neuen Skill (mit optionalem Proof-Cert) |
| `retrieve_skill` | Findet den besten Skill für einen gegebenen Task |
| `list_skills` | Listet Skills nach Domäne oder Verifikations-Status |
| `promote_experience` | Konvertiert eine ExperienceBus-Erfahrung zu einem Skill |
| `deprecate_skill` | Markiert einen Skill als veraltet (Audit-Trail) |

## Skill-Schema

```json
{
  "name": "binary_search_iterative",
  "description": "Iterative binary search for sorted arrays",
  "domain": "coding",
  "steps": ["Check bounds", "Calculate mid", "Compare and adjust", "Return result"],
  "verified": true,
  "proof_cert": "logicbrain:cert:abc123",
  "success_rate": 0.94,
  "usage_count": 47,
  "created": "2026-04-13"
}
```

## Verifikations-Tier

- `unverified` — Aus ExperienceBus promoted, noch nicht formal geprüft
- `structurally_sound` — Interne Konsistenz geprüft (kein LogicBrain-Cert)
- `verified` — LogicBrain ProofCertificate vorhanden ✅

## Stage 4 Acceptance Criterion

Skill-Reuse: ≥ 70% Success Rate beim Transfer einer gelernten Strategie auf neue ähnliche Tasks.

## Tech Stack

- Python 3.12
- FastAPI + MCP HTTP transport
- ChromaDB (semantische Skill-Suche)
- SQLite (Metadaten, Usage-Stats, Verifikations-Status)
- LogicBrain-Client (Verifikation)

## Deployment (Railway)

```
web: python -m skill_library.mcp_server_http
```

## Referenzen

- Voyager: Wang et al. (2023) — An Open-Ended Embodied Agent with LLMs
- SWE-bench Verified — Benchmark für Skill-Transfer
- `../ExperienceBus/` — Promotion-Quelle
- `../LogicBrain/` — Verifikations-Backend
- `../ROADMAP.md §4` — Vollständige Spec
