# Stage 4 Research Watch

Last reviewed: 2026-05-01

## Purpose

This document tracks external research breakthroughs that would unlock
further LogicBrain work toward Stage 4 (Learning Agent). It maps each
research gap to trigger conditions — specific developments that should
prompt new LogicBrain issues.

**When to check this document:** At the start of each development cycle,
or when a relevant paper/project appears.

**Background:** LogicBrain v0.8.0 ships the *verification substrate* for
Stage 4 — the infrastructure ensuring stored knowledge is sound
(CertificateStore, ProofExchangeNode, TrustLedger, VerifiedAgentRuntime,
AdversarialHarness). What it does **not** provide is the learning system
itself. The roadmap explicitly states: "These modules are primitives
toward verified memory, not a full learning system." The gaps below are
the research problems that stand between today's substrate and a genuine
Learning Agent.

---

## The Verifier-Learner Boundary

Before tracking research, it is essential to understand what LogicBrain's
Z3-backed verifier can and cannot check. This boundary defines where
LogicBrain should contribute and where it must defer to external systems.

| Z3 can check | Z3 cannot check |
|--------------|------------------|
| Logical consistency of learned rules ("does rule R contradict knowledge base K?") | Empirical correctness of heuristics ("does strategy S actually work?") |
| Policy conformance ("does behavior B violate safety policy P?") | Generalization quality ("will this transfer to unseen domains?") |
| Constraint satisfaction ("does the plan meet formal preconditions?") | Statistical calibration ("is the confidence score reliable?") |
| Contradiction detection in belief updates ("does the new belief conflict with proven facts?") | Causal validity ("does correlation reflect genuine causation?") |

**Implication:** LogicBrain can serve as a *logical guardrail* for a
learning agent — preventing logically inconsistent or policy-violating
knowledge — but cannot judge whether learned strategies are effective.
Effectiveness evaluation requires empirical feedback loops outside the
formal verification boundary.

---

## Research Gaps

### Gap 1: Stable Learning Without Drift

**The problem:** Catastrophic forgetting, reward hacking, and
distributional shift. No known algorithm reliably solves all three
simultaneously (see AGI Roadmap v2, Section 7).

**Stage 4 acceptance criteria at stake:**
- Memory stability: knowledge retention >= 90% after 1000 episodes
- Calibration over time: ECE decreasing or stable

**What to watch:**

| Project / Line of Research | Why it matters | Status (2026-05) |
|----------------------------|----------------|-------------------|
| Continual Learning with Elastic Weight Consolidation and successors | Prevents catastrophic forgetting in neural nets by penalizing changes to important weights | Active 2026: "EWC Done Right" (arxiv 2603.18596) fixes Fisher Information estimation; hybrid architecture achieves 0.8% vs EWC's 2.3% degradation per task. Apr 2026: Safe Continual RL (arxiv 2604.19737, Vanderbilt) empirically confirms a fundamental safety-forgetting tension — existing methods cannot simultaneously prevent forgetting AND satisfy safety constraints under non-stationary dynamics. No agent-level solution yet. |
| DPO successors (Rafailov et al., 2023) and reward-model-free alignment | Reduces reward hacking by eliminating explicit reward models | Active 2026: α-DPO (adaptive reward margin), PAR (+5pp win rate vs baselines). **ICLR 2026**: Alignment-Weighted DPO (arxiv 2602.21346) — segment-level preference weights target reasoning vs. answer separately; published conference paper, consistent empirical safety improvements. Stability at scale still unproven; formal bounds on policy drift absent. |
| GFlowNets (Bengio et al., 2021) | Diversity-preserving exploration that may resist mode collapse | Active research; integration in active learning loops exists (biosequence discovery, NeurIPS 2023); not yet in general agent learning loops. May 2026: Loss-Guided Auxiliary GFlowNets (LGGFN, arxiv 2505.15251) addresses mode collapse by directing exploration toward high-loss regions; still domain-specific (not general agent loops). |
| RLHF stability guarantees (Constitutional AI lineage) | Formal bounds on policy drift during online learning | Active 2026: First formal generalization analysis of KL-regularized RLHF (arxiv 2601.16403, Jan 2026). Formal bounds on online policy drift remain open. |
| LeanAgent (Anandkumar et al. / LeanDojo, 2023–2026) | Lifelong learning system for Lean 4 theorem proving — improves through experience across tasks | Active 2026: LeanDojo-v2 at NeurIPS 2025 workshop; LeanProgress (arxiv 2502.17925, Feb 2026) — proof progress prediction for search guidance. |
| **SafeAdapt** (Imperial College London, Apr 2026) | First formal, provable safety guarantees for policy updates in continual RL; Rashomon set certifies a safe region in policy parameter space around a source-task policy; projected gradient descent constrains downstream adaptation to remain within certified region | **New (2026-05)** — arxiv 2604.09452, Apr 10 2026. Only adaptation method achieving perfect source-task safety while maintaining competitive downstream performance; validated on grid-world navigation. Formal guarantee scoped to source-task distribution; cross-distribution safety bounds remain open. Not yet tested at scale. |

**Trigger condition for LogicBrain work:**
A published method demonstrating stable learning (retention >= 90%,
no reward hacking) across >= 100 diverse tasks would warrant building a
*verified learning loop* — a module where LogicBrain's consistency
checker gates each knowledge update from the learner.

**What LogicBrain would build:**
- `VerifiedMemoryGate`: intercepts knowledge updates, runs Z3
  consistency checks against existing CertificateStore, rejects
  contradictions
- Integration with `BeliefGraph` for monotonic belief update tracking
- Regression test harness measuring retention across update cycles

---

### Gap 2: Selective Retrieval with Relevance Weighting

**The problem:** CertificateStore provides storage and query-by-pattern,
but a learning agent needs to retrieve the *right* proof at the *right*
time. This requires relevance scoring, context-aware ranking, and
recency weighting — none of which are formal verification problems.

**Stage 4 acceptance criteria at stake:**
- Cross-task improvement >= 15% vs. cold start
- Skill reuse >= 70% on transfer tasks

**What to watch:**

| Project / Line of Research | Why it matters | Status (2026-05) |
|----------------------------|----------------|-------------------|
| Voyager skill library (Wang et al., 2023) | Demonstrates compositional skill storage and retrieval in Minecraft | Published; retrieval is embedding-based, not verified. No new developments. |
| Generative Agents reflective memory (Park et al., 2023) | Relevance + recency + importance scoring for episodic memory | Published; no formal verification of retrieved memories. No new developments. |
| RAG with structured knowledge graphs | Combines retrieval with graph-structured knowledge | Active 2026: GraphRAG mainstream; "Hierarchical Planning + KG-RAG + Symbolic Validation" (OpenReview); VeriRAG for Verilog hardware specs. Formal proof store integration still unexplored. |
| Verified retrieval (formal IR) | Retrieval algorithms with provable recall guarantees | Early stage 2026: Verifiable PIR research active in crypto domain (SNARKs-based); FIRE iterative retrieval for fact-checking. Not yet applicable to general knowledge bases. |
| **zkRAG** (IACR ePrint 2026/709, Apr 2026) | Zero-knowledge succinct non-interactive argument for RAG retrieval; proves that HNSW approximate-nearest-neighbor search was executed faithfully on a committed embedding database — no trust required in RAG-as-a-Service provider | **New (2026-05)** — Apr 12 2026. First PIOP tailored to the HNSW ANNS algorithm; 50 s to prove a query over 10^6 vectors (1000× faster than prior ZK baselines). Scope: cryptographic service consistency, not logical consistency. Does not address whether retrieved content is logically sound, only that the retrieval algorithm was followed faithfully. |
| **REAL-Prover** (arxiv 2505.20613, May 2026) | Open-source retrieval-augmented stepwise Lean 4 prover; semantic premise selection (LeanSearch-PS) + interactive Lean environment; SOTA on ProofNet (23.7% Pass@64) and FATE-M algebraic benchmark (56.7% Pass@64) | **New (2026-05)** — May 2026. Directly demonstrates retrieval-augmented proof synthesis for Lean 4 at scale; closest existing system to a verified retrieval API over a structured formal knowledge base. Open-source weights and tooling available. Relevant to LogicBrain's query_ranked and query_consistent APIs. |

**Trigger condition for LogicBrain work:**
A retrieval system demonstrating >= 80% relevant-proof-retrieval
precision on a structured knowledge base would warrant building a
verified retrieval API on top of CertificateStore.

**What LogicBrain has built (2026-03-29):**
- `CertificateStore.query_consistent(premises)` — Z3 consistency pre-filter
  (70% mean reduction in experiments, 100% precision on non-contradictory queries)
- `CertificateStore.query_ranked(query)` — Jaccard token-overlap relevance
  scoring for ranked retrieval
- Z3-checked retrieval invariant: consistency with current premises

**What remains:**
- Embedding-based or semantic retrieval ranker for non-propositional claims
- Usage-frequency and dependency-graph metadata

---

### Gap 3: Forgetting Policies

**The problem:** Indefinite accumulation of proofs and certificates will
eventually cause performance degradation and stale-knowledge conflicts.
A learning agent needs principled forgetting — deciding what to discard
without losing critical knowledge.

**Stage 4 acceptance criteria at stake:**
- Memory stability >= 90% (forgetting must be selective, not destructive)

**What to watch:**

| Project / Line of Research | Why it matters | Status (2026-05) |
|----------------------------|----------------|-------------------|
| Memory consolidation in cognitive architectures (SOAR, ACT-R) | Decades of research on selective forgetting in symbolic systems | Mature theory; limited integration with modern agents. No new 2026 developments. |
| Compression-based forgetting (information-theoretic) | Discard knowledge that is redundant given remaining knowledge | Theoretical; no agent implementation found in 2026 search. |
| Schema evolution / knowledge compaction | Merge multiple specific proofs into generalized rules | Active in database community; unexplored for proof stores. No 2026 bridge work found. |
| **Novel Memory Forgetting Techniques for Autonomous AI Agents** (arxiv 2604.02280, Apr 2026) | Formalizes adaptive memory regulation via relevance-weighted scoring, incremental updates, and constrained optimization under a fixed memory budget; integrates temporal decay for controlled long-horizon forgetting | **New (2026-05)** — Apr 2026. First paper in this cycle to formalize a forgetting policy as a constrained optimization problem with explicit budget and temporal decay. Not formally verified; operates over LLM context memory, not proof stores. Conceptually adjacent to dependency-aware pruning (the open work item in Gap 3). |

**Trigger condition for LogicBrain work:**
A demonstrated forgetting policy maintaining >= 95% task performance
while reducing stored knowledge by >= 50% would warrant extending
CertificateStore with verified pruning.

**What LogicBrain has built (2026-03-29):**
- `CertificateStore.compact()` — Z3-verified redundancy removal.
  Experiments showed 96–98% compaction at all difficulty levels with 100%
  conclusion preservation. Trigger condition met; module in production.

**What remains:**
- Dependency-aware pruning: never prune a certificate that others depend on
- `StoreStats` extended with staleness metrics and pruning audit trail

---

### Gap 4: Cross-Task Strategy Transfer

**The problem:** Storing proofs is not the same as transferring
*strategies*. A proof that "modus ponens applies to P->Q, P" does not
help with recognizing when modus ponens is *useful* in a new context.
Strategy transfer requires abstraction, analogy, and generalization —
capabilities outside formal verification.

**Stage 4 acceptance criteria at stake:**
- Skill reuse >= 70% on transfer tasks
- Cross-task improvement >= 15%

**What to watch:**

| Project / Line of Research | Why it matters | Status (2026-05) |
|----------------------------|----------------|-------------------|
| Voyager (Wang et al., 2023) | Skill library with compositional reuse | Published; skills are code snippets, not verified. No new developments. |
| Program synthesis for strategy abstraction | Abstract specific solutions into reusable templates | No 2026 developments found; DreamCoder/LAPS last active 2021. Open problem. |
| Analogical reasoning in LLMs | LLMs can draw structural analogies | Capability exists but is unreliable and unverified. No new 2026 results. |
| Proof-strategy libraries (Isabelle, Lean tactics) | Formal proof assistants already have tactic libraries | Mature; but human-curated, not learned. |
| **Leanstral** (Mistral AI, 2026-03) | First open-source LLM agent specifically trained on Lean 4 repositories; 6B params, Apache 2.0, MCP-compatible; learns to apply tactics across real-world Lean codebases | Active: competitive with Claude Sonnet at fraction of cost (pass@2 = 26.3 vs Sonnet's 23.7; pass@16 = 31.9 vs Sonnet's 23.9; $36 vs $549 per run). MCP support enables integration with LogicBrain toolchain. No new major updates since Mar 2026 release. |
| LeanCopilot / LeanDojo (Anandkumar Lab, 2023–2026) | Retrieval-augmented LLM proof assistant; LeanDojo provides structured access to Lean repos for training and inference | Active 2026: LeanDojo-v2 at NeurIPS 2025 workshop; LeanProgress (arxiv 2502.17925, Feb 2026 v3) — proof progress prediction improves tactic search efficiency (+3.8% on Mathlib4). |
| **BRIDGE** (arxiv 2511.21104, Nov 2025 / updated Feb 2026) | Structured prompting framework for domain-guided program synthesis; decomposes verification into Code, Specifications, and Theorem Statements as interconnected domains; elicits domain-specific intermediate reasoning to connect them | **New (2026-05)** — arxiv 2511.21104. Improves Lean executable correctness ~1.5× (Pass@5) over direct baselines; 2× more sample-efficient at inference; SFT on BRIDGE traces yields ~1.5× higher Lean pass than code-only SFT. Addresses the strategy abstraction problem by bridging informal intent and formal proof structure — directly relevant to ProofTemplate work. |
| **Goedel Prover / Awakening the Sleeping Agent** (arxiv 2604.08388, Apr 2026) | Shows that Lean-specific agentic training data "reactivates" latent general tool-use capability in a prover; fine-tuning on Lean-specific trajectories dramatically improves tactic application without sacrificing generality | **New (2026-05)** — Apr 2026. Demonstrates that domain-specific agentic data (Lean 4 tactic traces) transfers to general tool use; complements Leanstral and REAL-Prover. Relevant to understanding how tactic strategy libraries can be learned rather than hand-curated. |

**Trigger condition for LogicBrain work:**
A system demonstrating verified strategy transfer — where an agent
reuses a *proven* approach from task A on task B with a formal guarantee
that the approach is applicable — would warrant building a strategy
abstraction layer.

**What LogicBrain would build:**
- `ProofTemplate`: generalized certificate with holes (universally
  quantified variables) that can be instantiated for new tasks
- Z3-checked template instantiation: verify that substituting specific
  values preserves validity
- Integration with `ProofOrchestrator` for compositional strategy reuse

---

## Experimental Validation (v0.8.0 Substrate)

Experiments #77–#80 tested the v0.8.0 substrate under realistic
conditions. Results inform which production modules are worth building.

### Results Summary

| Experiment | Question | Result |
|------------|----------|--------|
| #77 Memory Consistency | Does CertificateStore scale? | Yes — 500 certs in 1.9s, 0 errors, 5/5 contradictions detected |
| #78 Entailment Compaction | Can Z3 detect redundancy? | Yes — 98.75% compaction (80 → 1 cert at EASY) |
| #79 Compaction Curve | Only effective for simple knowledge? | No — 96–98% compaction at ALL difficulty levels (EASY through EXTREME) |
| #80 Context Retrieval | Can Z3 filter for relevance? | Partially — consistency filter useful (70% mean reduction), but consistency ≈ applicability for random propositional logic |

### Key Findings

**Compaction (#78/#79):**
- Z3-based entailment compaction reduces proof stores by 96–98% while
  preserving all provable conclusions. This holds across all difficulty
  levels (3–6 variables, 3–8 premises).
- The extreme compaction ratio reflects high logical interconnection in
  randomly generated propositional logic. Real-world proofs from diverse
  domains would likely show lower compaction.
- Performance scales linearly: 2.7s (EASY) → 11.4s (EXTREME) for 100 certs.
- **Conclusion:** `CertificateStore.compact()` is viable as a production
  feature. Z3 can reliably identify and remove redundant certificates.

**Retrieval (#80):**
- Z3 consistency filtering eliminates 70% of stored certificates on
  average per query — but this is inflated by queries with contradictory
  premises (10/18 queries, 100% filtered).
- For non-contradictory queries, consistency ≈ applicability (precision
  = 100%). The two filter levels collapse because the knowledge base is
  highly interconnected.
- Z3 excels at detecting inconsistent queries ("is this question even
  coherent?") — valuable as a pre-filter.
- **Conclusion:** A simple consistency-based retrieval filter is
  production-ready. The applicability filter adds no value for random
  propositional logic but may matter for structurally diverse knowledge
  bases (different domains, different variable sets).

### Impact on Research Gaps

| Gap | Before Experiments | After Experiments | 2026-05 Update |
|-----|-------------------|-------------------|----------------|
| Gap 1 (Stable Learning) | Trigger: external breakthrough needed | Unchanged — still requires external breakthrough | SafeAdapt (Apr 2026) provides first formal provable safety guarantee for continual RL policy updates (Rashomon set certification). Closest external advance yet, but scoped to source-task distribution only. Trigger condition (retention >= 90%, no reward hacking, >= 100 tasks) not met. |
| Gap 2 (Retrieval) | Trigger: >= 80% precision on structured KB | **Partially met** — Z3 consistency filter achieves this for propositional logic; needs testing on diverse/multi-domain KBs | REAL-Prover (May 2026) achieves SOTA retrieval-augmented proving on Lean 4 (56.7% on algebraic benchmark). zkRAG (Apr 2026) proves RAG retrieval cryptographically. Neither meets the trigger directly, but both advance the art of formal retrieval in proof contexts. |
| Gap 3 (Forgetting) | Trigger: >= 95% performance at >= 50% reduction | **Met** — Z3 compaction achieves 96–98% reduction with 100% conclusion preservation | Novel Memory Forgetting (Apr 2026) formalizes constrained-budget adaptive forgetting for LLM agents — conceptually aligned with dependency-aware pruning (open work item). |
| Gap 4 (Strategy Transfer) | Trigger: verified transfer with formal guarantee | **Experimentally validated** — uniform substitution achieves 100% transfer rate (21/21 valid, 6/6 invalid preserved). See `tests/experiments/test_proof_template_transfer.py` | BRIDGE (Feb 2026) and Goedel Prover (Apr 2026) advance learned tactic strategy abstraction in Lean 4; BRIDGE's domain decomposition is conceptually related to ProofTemplate instantiation. External validation of the strategy-abstraction direction. |

### Recommended Next Steps (Production Modules)

Based on experimental results, the following modules have been built:

1. **`CertificateStore.compact()`** — ✅ Built (2026-03-22). Z3-verified
   redundancy removal. Gap 3 trigger condition met.
2. **`CertificateStore.query_consistent(premises)`** — ✅ Built (2026-03-22).
   Z3 consistency pre-filter. Gap 2 partially met.
3. **`CertificateStore.query_ranked(query)`** — ✅ Built (2026-03-29).
   Jaccard token-overlap relevance scoring.
4. **ProofTemplate experiment** — ✅ Validated (2026-03-29). 100% transfer
   rate via uniform substitution. A `ProofTemplate` production module is
   now justified. See Gap 4 section.

---

## What LogicBrain Already Provides (v0.8.0)

These modules form the verification substrate that any Stage 4 work
would build on:

| Module | Role in Stage 4 |
|--------|-----------------|
| `CertificateStore` | Persistent proof memory with query API |
| `ProofCertificate` | Serializable, verifiable reasoning records |
| `ProofExchangeNode` | Cross-agent proof bundles with schema versioning |
| `TrustLedger` | Federated trust-domain verification |
| `VerifiedAgentRuntime` | Closed-loop request/response with proof requirements |
| `AdversarialHarness` | Adversarial self-play for robustness testing |
| `BeliefGraph` | Causal belief tracking with contradiction detection |
| `AssumptionSet` | Typed epistemic state (fact / assumption / hypothesis) |
| `GoalContract` | Machine-checkable preconditions and postconditions |
| `ActionPolicyEngine` | Pre-action policy enforcement |

---

## The Learner-Governor Problem

A meta-concern for Stage 4: a learner that can modify its own safety
governor is potentially dangerous (mesa-optimization; Hubinger et al.,
2019). A learner that cannot modify its governor may be too constrained
to reach general intelligence. This tension has no known clean solution.

**LogicBrain's position:** The verifier (Z3) is *external* to the
learner — it checks claims but does not generate them. This architecture
naturally separates learning from governance. Any Stage 4 extension
must preserve this separation: the learner proposes, the verifier
disposes.

---

## Review Schedule

- **Quarterly:** Scan arxiv, major ML conferences (NeurIPS, ICML, ICLR),
  and agent-systems workshops for papers matching the trigger conditions
  above.
- **On event:** When a project in the watch tables releases code or
  benchmarks, evaluate against the trigger conditions.
- **Update this document** whenever a trigger condition is met or a
  watched project materially changes status.
