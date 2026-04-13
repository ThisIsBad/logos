# AGI Tool Stack — Roadmap

**Erstellt:** 2026-04-13  
**Basis:** `LogicBrain/docs/agi_roadmap_v2.md` (Claude Opus 4.6, 2026-03-20)  
**Status:** Living document

---

## 1. Ausgangslage & Kernthese

> AGI entsteht nicht durch Skalierung allein. Ein plausiblerer Pfad ist eine
> **koordinierte kognitive Architektur**: Foundation Model + persistentes Gedächtnis
> + Planning + Verifikation + Grounding + aktives Lernen + Ziel-Governance.
>
> — `agi_roadmap_v2.md §2`

LLMs sind probabilistische Token-Generatoren. Sie brauchen deterministische
Leitplanken. Dieser Tool Stack liefert diese Leitplanken als deploybare MCP-Services.

---

## 2. AGI Stage Map

| Stage | Bezeichnung | Status | Schlüssel-Capabilities |
|-------|-------------|--------|----------------------|
| **1** | Language Agent | ✅ Erreicht | MMLU ≥85%, HumanEval ≥85% |
| **2** | Tool Agent | ✅ Erreicht | MCP-Tools, LogicBrain deployed |
| **3** | Reflexive Agent | 🔶 In Arbeit | Planning, Persistenz, Kalibrierung |
| **4** | Learning Agent | 🔬 Forschung | Episodisches Lernen, Skill-Akkumulation |
| **5** | General Cognitive | 🔭 Ziel | Cross-Domain Transfer, stabile Agency |

---

## 3. Gap-Analyse: Was fehlt

Aus `agi_roadmap_v2.md §3.1` — 8 Module für AGI, Mapping auf diesen Stack:

| Gap | Warum LLMs allein nicht reichen | Service in diesem Stack |
|-----|----------------------------------|------------------------|
| Verifikation | Plausibel ≠ korrekt, kein Falsifikations-Mechanismus | **LogicBrain** ✅ |
| Ziel-Governance | Ohne explizite Ziel-Repräsentation: Drift | **LogicBrain** (GoalContract) + **DriftGuard** |
| Persistentes Gedächtnis | Context Windows sind ephemer, kein lifelong learning | **MemoryBrain** |
| Planning & Search | Autoregressive Planung, kein State-Space-Search | **PlannerBrain** |
| Selbst-Modellierung | Kalibrierung ist ungelöstes Problem, aber strukturell lösbar | **SelfModel** |
| Welt-Modellierung | Korrelationen ≠ Kausalstruktur, kein Do-Calculus | **WorldModel** |
| Aktives Lernen | Kein Exploration-Exploitation-Loop nach Deployment | **ExperienceBus** |
| Skill-Akkumulation | Strategien sind nicht persistent speicherbar/abrufbar | **SkillLibrary** |

---

## 4. Service-Übersicht

### Phase 1 — Stage 3 Completion (Reflexive Agent)

#### `MemoryBrain` — Persistentes Gedächtnis

**AGI-Lücke:** Lifelong knowledge accumulation  
**Inspiration:** RETRO (Borgeaud et al., 2022), Generative Agents (Park et al., 2023)

**Architektur:**
- Episodisches Gedächtnis: Was ist wann passiert? (zeitlich geordnet)
- Semantisches Gedächtnis: Was ist wahr/bekannt? (konzeptuell strukturiert)
- Verifizierte Erinnerungen: Memories mit LogicBrain-ProofCertificate → `proven=True`
- Konsolidierung: ähnliche Memories werden periodisch zusammengefasst
- Vergessen: Relevanz-basiertes Decay

**MCP-Tools:**
```
store_memory(content, type, confidence, proof_cert?)
retrieve_memory(query, k=5, min_confidence=0.7, type?)
consolidate()
forget(memory_id, reason)
list_proven_beliefs()
get_memory_stats()
```

**Stack:** Python 3.12 + ChromaDB (Vector) + SQLite (Metadaten) + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

#### `PlannerBrain` — Hierarchisches Planning & Search

**AGI-Lücke:** Planning und Backtracking  
**Inspiration:** Tree of Thoughts (Yao et al., 2023), RAP (Hao et al., 2023)

**Architektur:**
- Ziel-Dekomposition: Goal → Sub-Goals → Steps (hierarchisch)
- Tree-of-Thoughts Search mit Kosten-Pruning
- Plan-Verifikation via LogicBrain (GoalContract pre/postconditions)
- Backtracking wenn ein Pfad scheitert
- Plan-History für Debugging

**MCP-Tools:**
```
decompose_goal(goal, context, max_depth?) → plan_tree
evaluate_step(step, current_state) → {feasible, confidence, risks}
backtrack(plan_id, failed_step_id) → alternative_branches
verify_plan(plan_id) → LogicBrain GoalContract check
commit_step(plan_id, step_id, outcome)
get_plan(plan_id)
```

**Stack:** Python 3.12 + NetworkX (Graphstruktur) + LogicBrain-Client + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

### Phase 2 — Stage 3→4 Bridge

#### `SelfModel` — Metakognition & Kalibrierung

**AGI-Lücke:** Self-modeling, Uncertainty estimation  
**Inspiration:** Kadavath et al. (2022), Lin et al. (2022)

**Architektur:**
- Unsicherheits-Tracking pro Domäne (Coding, Mathematik, Faktenwissen, ...)
- Confidence vs. Actual Accuracy über Zeit → ECE-Berechnung
- Kompetenz-Map: systematische Fehler-Muster pro Bereich
- Eskalations-Trigger bei Konfidenz unter Schwellwert

**MCP-Tools:**
```
log_prediction(claim, confidence, domain)
log_outcome(claim_id, was_correct)
get_calibration(domain?) → {ece, bias, sharpness, n_samples}
should_escalate(claim, confidence, domain) → {escalate: bool, reason}
get_competence_map() → {domain → accuracy_estimate}
```

**Stack:** Python 3.12 + SQLite + scipy (ECE) + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

#### `WorldModel` — Kausales Reasoning (Do-Calculus)

**AGI-Lücke:** World modeling, causal structure  
**Inspiration:** Pearl (2000, 2009), Schölkopf et al. (2021)

**Architektur:**
- Kausaler Graph: Knoten (Variable/Action/Outcome/Context) + gerichtete Kanten
- Pearl's 3-Ebenen: Assoziation P(Y|X) → Intervention P(Y|do(X)) → Kontrafaktisch
- Interventions-Simulation: `do(X=x)` → Downstream-Effekte propagieren
- Integration mit LogicBrain `counterfactual_branch` für formale Absicherung

**MCP-Tools:**
```
add_causal_edge(cause, effect, strength, evidence?, domain?)
compute_intervention(action, context) → {outcomes, confidence}
counterfactual(world_state, hypothetical_action) → {delta, affected_nodes}
query_causes(effect, max_depth?) → causal_chain
get_causal_graph(domain?) → graph_snapshot
```

**Stack:** Python 3.12 + NetworkX + pgmpy + LogicBrain-Client + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

### Phase 3 — Stage 4: Learning Agent

#### `ExperienceBus` — Erfahrungs-Akkumulation

**AGI-Lücke:** Active learning, cross-task improvement  
**Inspiration:** Reflexion (Shinn et al., 2023), GAIA Benchmark

**Architektur:**
- Jede Agent-Aktion wird mit Outcome gespeichert
- Mustererkennung über ähnliche Erfahrungen
- "Lessons Learned" für zukünftige Tasks abrufbar
- Kandidaten für SkillLibrary-Promotion identifizieren

**MCP-Tools:**
```
record_experience(task, action, outcome, context, success: bool)
retrieve_lessons(task_description, k=3) → similar_experiences + lessons
extract_patterns(domain?) → {failure_patterns, success_patterns}
get_skill_candidates(min_success_rate=0.8) → promotion_candidates
```

**Stack:** Python 3.12 + SQLite + ChromaDB (Similarity) + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

#### `SkillLibrary` — Verified Skill Storage

**AGI-Lücke:** Skill-Akkumulation, Strategie-Wiederverwendung  
**Inspiration:** Voyager (Wang et al., 2023) — Minecraft-Agent mit persistenter Skill-Bibliothek

**Architektur:**
- Skills = bewährte Strategien als wiederverwendbare, benannte Prozeduren
- Nur Skills mit LogicBrain-ProofCertificate → `verified=True`
- Semantische Suche: "Finde Skill für Task X"
- Promotion-Pipeline: ExperienceBus → SkillLibrary

**MCP-Tools:**
```
store_skill(name, description, steps, domain, proof_cert?)
retrieve_skill(task_description, domain?) → best_match + confidence
list_skills(domain?, verified_only=False)
promote_experience(experience_id) → skill_id
deprecate_skill(skill_id, reason)
```

**Stack:** Python 3.12 + ChromaDB + SQLite + LogicBrain-Client + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

#### `DriftGuard` — Ziel-Stabilitäts-Monitor

**AGI-Lücke:** Goal stability, mesa-optimization prevention  
**Inspiration:** Omohundro (2008), Hubinger et al. (2019)

**Architektur:**
- Registrierte Ziele mit Constraints (via LogicBrain GoalContract)
- Jede Aktion wird gegen aktive Ziele geprüft
- Drift-Score über Zeit: Wie stark weicht das Verhalten vom Ziel ab?
- Automatischer Alert bei Schwellwert-Überschreitung

**MCP-Tools:**
```
register_goal(description, constraints, priority?) → goal_id
check_action_alignment(action, goal_id) → {aligned: bool, drift_score, reason}
get_drift_history(goal_id, window?) → timeline
alert_misalignment(goal_id, action, severity) → alert_id
list_active_goals() → goals
```

**Stack:** Python 3.12 + SQLite + LogicBrain-Client + FastAPI + MCP  
**Status:** 🔲 Nicht implementiert

---

## 5. Deployment-Architektur

```
Railway Services:
┌─────────────────────────────────────────────────────┐
│  logicbrain.railway.app     [DEPLOYED ✅]            │
│  memorybrain.railway.app    [Phase 1 — next]        │
│  plannerbrain.railway.app   [Phase 1]               │
│  selfmodel.railway.app      [Phase 2]               │
│  worldmodel.railway.app     [Phase 2]               │
│  experiencebus.railway.app  [Phase 3]               │
│  skilllibrary.railway.app   [Phase 3]               │
│  driftguard.railway.app     [Phase 3]               │
└─────────────────────────────────────────────────────┘

Kommunikation:
- Jeder Service: HTTP REST + MCP transport (/mcp endpoint)
- LogicBrain als optionaler Verifikations-Backend für alle Services
- Kein direktes Service-zu-Service-Calling (Claude orchestriert)
```

Jeder Service folgt dem LogicBrain-Deployment-Muster:
```
<service>/
├── Dockerfile           # FROM python:3.12-slim
├── Procfile             # web: python -m <service>.mcp_server_http
├── railway.toml         # healthcheckPath = "/health"
├── pyproject.toml       # [http] extras: mcp, uvicorn, starlette
├── <service>/
│   ├── __init__.py
│   ├── core.py          # Kern-Logik
│   └── mcp_server_http.py  # FastAPI + MCP endpoint
└── tests/
    └── test_core.py
```

---

## 6. Build-Priorität

| Prio | Service | Lücke | Aufwand | Impact |
|------|---------|-------|---------|--------|
| **1** | `MemoryBrain` | Persistenz | Mittel | Sehr hoch |
| **2** | `PlannerBrain` | Planning | Mittel-Hoch | Hoch |
| **3** | `SelfModel` | Kalibrierung | Niedrig | Hoch |
| **4** | `WorldModel` | Kausalität | Hoch | Hoch |
| **5** | `ExperienceBus` | Lernen | Niedrig | Mittel (Stage 4) |
| **6** | `SkillLibrary` | Skills | Mittel | Mittel (Stage 4) |
| **7** | `DriftGuard` | Drift | Niedrig | Mittel (LogicBrain-Extension) |

---

## 7. Stage 3 Acceptance Criteria (Ziel für Phase 1+2)

Aus `agi_roadmap_v2.md §4.3`:

| Kriterium | Benchmark | Schwellwert |
|-----------|-----------|-------------|
| Novel task generalization | ARC-AGI | ≥ 50% |
| Self-evaluation calibration | ECE auf 200 Claims | ≤ 0.10 |
| Multi-step planning | ALFWorld / WebArena | ≥ 60% success |
| Error self-detection | 100 gesäte Fehler | ≥ 30% erkannt |
| Replanning after failure | Re-attempt success rate | ≥ 50% |

---

## Changelog

| Datum | Änderung |
|-------|----------|
| 2026-04-13 | Initiale Roadmap erstellt, Konzept mit Stefan besprochen |
