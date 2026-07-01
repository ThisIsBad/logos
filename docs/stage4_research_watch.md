# Stage 4 Research Watch

Last reviewed: 2026-07-01

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

| Project / Line of Research | Why it matters | Status (2026-07) |
|----------------------------|----------------|-------------------|
| Continual Learning with Elastic Weight Consolidation and successors | Prevents catastrophic forgetting in neural nets by penalizing changes to important weights | Active 2026: "EWC Done Right" (arxiv 2603.18596) **accepted to CVPR 2026** (Mar 2026); introduces Logits Reversal (LR) operation to fix Fisher Information estimation (gradient vanishing + inaccurate importance); significantly outperforms EWC variants. Hybrid architecture achieves 0.8% vs EWC's 2.3% degradation per task. No agent-level solution yet demonstrating >=100 diverse tasks. **Context Channel Capacity Framework** (arXiv 2603.07415, Mar 2026) formally proves the "Impossibility Triangle": zero forgetting, online learning, and finite parameters cannot simultaneously hold; defines C_ctx (context channel capacity) = mutual information between context signal and parameters; validates across 8 CL methods on Split-MNIST (1,130+ experiments), showing C_ctx perfectly predicts forgetting behavior. |
| DPO successors (Rafailov et al., 2023) and reward-model-free alignment | Reduces reward hacking by eliminating explicit reward models | Active 2026: **Gate-DPO** (arxiv 2605.02626, May 2026) addresses DPO's probability-collapse "squeezing effect" by gating rejected gradients based on the model's probability geometry; smaller gated models outperform larger ungated ones, suggesting gradient control > scale for stability. α-DPO, PAR remain active. Formal bounds on policy drift still absent. **POET** (arXiv 2506.09457, ACL 2026 Findings) addresses "reward-generation gap" in DPO/SimPO via prefix-oriented equal-length training; +11.8pp on AlpacaEval 2. **Confident Layer Decoding** (arXiv 2606.21906, Jun 20, 2026) mitigates alignment tax via entropy-guided backward layer search; gains on GPQA-Diamond, Omni-MATH, HLE with <2% latency increase and zero memory overhead. |
| GFlowNets (Bengio et al., 2021) | Diversity-preserving exploration that may resist mode collapse | Active 2026: **Goal2FlowNet** (OpenReview) uses GFlowNets to learn exploratory goal-conditioned policy covers, improving sample complexity and zero-shot generalisation for goal-conditioned RL. Integration in general agent learning loops still limited. **GFlowNet-OT** (arXiv 2606.06272, Jun 4, 2026, ICML 2026 SPIGM Workshop) establishes that non-acyclic GFlowNets solve optimal transport when configured as minimum-flow systems; minimum-flow GFlowNet objective reduces to Kantorovich OT problem with graph-induced shortest paths; enables large-scale graph OT via neural edge-flow parameterization. **PPO for GFlowNets** (arXiv 2606.15793, Jun 14, 2026) first derives and applies PPO to GFlowNets; improved convergence speed and data efficiency vs. standard GFlowNet objectives on synthetic energy functions and molecular graph generation. Theoretical foundations now much stronger; agent-loop integration still limited. |
| RLHF stability guarantees (Constitutional AI lineage) | Formal bounds on policy drift during online learning | Active 2026: arxiv 2601.16403 (Jan 2026) — first formal analysis of KL-regularized RLHF. **"A Tighter Bound for Reward Learning in RLHF"** (ICLR 2026, OpenReview forum EyMoFzI3Oz) and **"Provably Efficient Online RLHF with One-Pass Reward Modeling"** (arxiv 2502.07193) published. Formal bounds on online policy *drift* remain open; bounds address reward learning and convergence, not drift across deployment. **Explaining and Preventing Alignment Collapse in Iterative RLHF** (arXiv 2605.04266, May 7, 2026; Bach, Jordan) — formal bounds (Theorems 2.1, 3.1–3.6) characterizing collapse conditions and convergence rates; influence-function-based prevention strategy for maintaining alignment stability. Closest yet to formal bounds on iterative policy drift; deployment drift across diverse tasks remains open. |
| LeanAgent (Anandkumar et al. / LeanDojo, 2023–2026) | Lifelong learning system for Lean 4 theorem proving — improves through experience across tasks | Active 2026: ICLR 2025 paper; **LeanProgress v3** (arxiv 2502.17925v3) code merged into LeanDojo-v2 (confirmed May 2026); 75.8% proof progress prediction accuracy (MAE 3.15 steps with history), +3.8pp on Mathlib4 proof search vs baseline of 41.4%. |
| **ProgAgent** (arxiv 2603.07784, Mar 2026) | Continual RL agent deriving dense shaped rewards from unlabeled expert videos; directly addresses catastrophic forgetting + reward specification cost | **New (2026-06)** — outperforms key baselines on ContinualBench and Meta-World; real-robot trials validate complex manipulation skill learning. Robotic domain only; no extension to general agent reasoning loops yet. |

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

| Project / Line of Research | Why it matters | Status (2026-07) |
|----------------------------|----------------|-------------------|
| Voyager skill library (Wang et al., 2023) | Demonstrates compositional skill storage and retrieval in Minecraft | Published; retrieval is embedding-based, not verified. No new developments. |
| Generative Agents reflective memory (Park et al., 2023) | Relevance + recency + importance scoring for episodic memory | Published; no formal verification of retrieved memories. No new developments. |
| RAG with structured knowledge graphs | Combines retrieval with graph-structured knowledge | Active 2026: GraphRAG mainstream; "Hierarchical Planning + KG-RAG + Symbolic Validation" (OpenReview); **CRAMF** (arxiv 2508.06931, concept-driven retrieval-augmented mathematical formalization) enhances LLM autoformalization by retrieving formal definitions of core mathematical concepts. Formal proof store integration still unexplored. |
| Verified retrieval (formal IR) | Retrieval algorithms with provable recall guarantees | Early stage 2026: Verifiable PIR research active in crypto domain (SNARKs-based); FIRE iterative retrieval for fact-checking. Not yet applicable to general knowledge bases. |
| **REAL-Prover** (arxiv 2505.20613, Leansearch-PS) | Retrieval-augmented open-source Lean 4 prover; combines fine-tuned LM with Leansearch-PS retrieval component for college-level math | **New (2026-06)** — 23.7% on ProofNet (Pass@64); **56.7% on FATE-M algebraic benchmark (new SOTA)**. Retrieval is for premise/lemma lookup, not verified retrieval. Precision on structured proof stores not yet reported. |
| **LeanSearch v2** (arXiv 2605.13137, May 14, 2026) | Global premise retrieval for Lean 4 theorem proving; two-mode operation (standard + reasoning-aware); open-sourced code, data, and benchmarks | **New (2026-07)** — 46.1% recovery of ground-truth premise groups within 10 candidates on 69 research-level Mathlib4 theorems (vs. 38.0% reasoning-system baseline and 9.3% premise-selection baseline); integrated with fixed prover loop achieves 20% proof success vs. 16% with next-best system. Most capable open premise-retrieval system for Lean 4 to date; precision on structured proof stores not yet reported. |

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

| Project / Line of Research | Why it matters | Status (2026-07) |
|----------------------------|----------------|-------------------|
| Memory consolidation in cognitive architectures (SOAR, ACT-R) | Decades of research on selective forgetting in symbolic systems | Mature theory; limited integration with modern agents. No new 2026 developments. |
| Compression-based forgetting (information-theoretic) | Discard knowledge that is redundant given remaining knowledge | **Active 2026**: **Memanto** (arxiv 2604.22085, Apr 2026) — typed semantic memory with 13-category schema, automated conflict resolution, temporal versioning, information-theoretic search (no indexing); 89.8% on LongMemEval, 87.1% on LoCoMo, new SOTA. **Temporal Memory for Resource-Constrained Agents** (arxiv 2604.00067, Apr 2026) — stochastic compress-add-smooth framework for continual learning under memory budget. **Memory Bank Compression for CL in LLMs** (arxiv 2601.00756, Jan 2026) — codebook-based compression of memory banks. First concrete agent implementations with IT compression now published. |
| Schema evolution / knowledge compaction | Merge multiple specific proofs into generalized rules | Active in database community; unexplored for proof stores. No 2026 bridge work found. |
| **Active Context Compression / Focus Agent** (arXiv 2601.07190, Jan 2026) | Autonomous memory management in LLM agents; "Focus Agent" consolidates learnings into persistent Knowledge blocks without human intervention | Early 2026: 22.7% average token reduction while maintaining task accuracy; up to 57% token savings on individual instances; averages 6.0 autonomous compressions per task. Complements information-theoretic approaches (Memanto); not yet applied to proof stores. |
| **Memanto** (arxiv 2604.22085, Apr 2026) | Universal typed semantic memory for long-horizon agents; automated conflict resolution + temporal versioning + information-theoretic retrieval (no separate vector index required) | **New (2026-06)** — SOTA on LongMemEval (89.8%) and LoCoMo (87.1%), surpassing graph+vector hybrids with a single retrieval query and zero ingestion cost. Architecture is analogous to what a LogicBrain-backed store would need for agent-facing retrieval; conflict resolution maps directly to Z3 consistency checking. |

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

| Project / Line of Research | Why it matters | Status (2026-07) |
|----------------------------|----------------|-------------------|
| Voyager (Wang et al., 2023) | Skill library with compositional reuse | Published; skills are code snippets, not verified. No new developments. |
| Program synthesis for strategy abstraction | Abstract specific solutions into reusable templates | No 2026 DreamCoder/LAPS successors found. LILO (ICLR 2024) — library learning via compression + LLM documentation — remains most recent practical successor; no 2026 update. Open problem. |
| Analogical reasoning in LLMs | LLMs can draw structural analogies | Capability exists but is unreliable and unverified. No new 2026 results. |
| Proof-strategy libraries (Isabelle, Lean tactics) | Formal proof assistants already have tactic libraries | Mature; but human-curated, not learned. |
| **Leanstral** (Mistral AI, 2026-03 → 2026-06) | First open-source LLM agent specifically trained on Lean 4 repositories; 6B params (119B total, MoE), Apache 2.0, MCP-compatible; learns to apply tactics across real-world Lean codebases | Active 2026: pass@2 = 26.3 (v26.03), beats Claude Sonnet 3.7 by 2.6 points at ~1/15 the cost ($36 vs $549). MCP support enables integration with LogicBrain toolchain. **v26.03 retired June 30, 2026; Leanstral 1.5 (v26.06) released June 2026** — successor MoE model; FLTEval benchmarks for v26.06 not yet published. Still no verified strategy-transfer guarantee. |
| LeanCopilot / LeanDojo (Anandkumar Lab, 2023–2026) | Retrieval-augmented LLM proof assistant; LeanDojo provides structured access to Lean repos for training and inference | Active 2026: **LeanDojo-v2 released April 26, 2026** — end-to-end framework combining repository tracing, lifelong dataset management, retrieval-augmented agents, Hugging Face fine-tuning, and external inference APIs; **LeanProgress v3** (arxiv 2502.17925v3) code merged into LeanDojo-v2 (confirmed May 2026); 75.8% proof progress prediction accuracy, +3.8pp on Mathlib4 search (from 41.4% baseline). |
| **MA-LoT** (arxiv 2503.03205, Mar 2025 / v3 May 2025) | Multi-agent Lean 4 prover using long chain-of-thought; separates proof generation from error-analysis via multi-LLM collaboration; LoT-Transfer Learning avoids need for annotated data | **New (2026-06)** — 61.07% on MiniF2F-Test (Lean 4), outperforming DeepSeek-V3 (33.61%), InternLM-Step-Prover (50.70%), and Godel-Prover (55.33%). Strategies are LLM-generated, not verified. Relevant as a benchmark baseline for Leanstral / LeanCopilot comparisons. |
| **Lean4Agent** (arXiv 2606.06523v2, Jun 15, 2026) | First comprehensive framework applying Lean 4 dependent-type formal language to LLM agent behavior verification; introduces **FormalAgentLib** — extensible Lean 4 library for formally modeling and verifying agent workflows and trajectories via three-layer verification (structural, semantic, trajectory) | **New (2026-07)** — workflows passing semantic verification outperformed failing ones by **14.80%** on software engineering tasks and **9.07%** on paper understanding tasks; LeanEvolve refinement method adds 7.47% average improvement on engineering problems. Direct relevance to LogicBrain: FormalAgentLib is the first Lean 4 substrate for agent workflow verification analogous to what Stage 4 would require. Verifies workflow structure and trajectory validity, not strategy applicability; no verified strategy-transfer guarantee yet. |
| **MiniF2F SOTA cluster** (2026) | Kimina-Prover 92.2%, Goedel-Prover-V2 90.4%, DeepSeek-Prover-V2 88.9% on MiniF2F; machine-verified Fermat-Goldbach–Gutmann quantum conjecture (arXiv 2606.29687, Jun 2026) using Claude AI + Lean 4 demonstrates frontier AI discovering and machine-verifying novel research-level proofs | **New (2026-07)** — MiniF2F is approaching saturation; community benchmark focus shifting to research-level theorems (Mathlib4, PutnamBench, domain-specific libraries). Quantum conjecture result (ICML 2026 context) shows real-world formal-proof impact. All systems generate LLM-produced tactics; none provide verified strategy-transfer guarantees. |

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

| Gap | Before Experiments | After Experiments | 2026-07 Update |
|-----|-------------------|-------------------|----------------|
| Gap 1 (Stable Learning) | Trigger: external breakthrough needed | Unchanged — still requires external breakthrough | Gate-DPO (May 2026) improves DPO stability; EWC Done Right (CVPR 2026); ProgAgent shows continual RL progress. **Jul 2026:** Alignment Collapse in Iterative RLHF (arXiv 2605.04266) provides formal bounds on collapse conditions — closest yet to deployment drift bounds; GFlowNet-OT and PPO-GFlowNets (Jun 2026) advance theoretical foundations; Context Channel Capacity Framework (Mar 2026) proves catastrophic forgetting unavoidable under finite parameters. Trigger (>=100 diverse tasks, no reward hacking, no drift) still not met. |
| Gap 2 (Retrieval) | Trigger: >= 80% precision on structured KB | **Partially met** — Z3 consistency filter achieves this for propositional logic; needs testing on diverse/multi-domain KBs | REAL-Prover and CRAMF advance retrieval-augmented Lean proving. **Jul 2026:** LeanSearch v2 (arXiv 2605.13137, May 2026) achieves 46.1% premise-group recovery within 10 candidates on Mathlib4 research theorems and 20% proof success with fixed prover — best open structured-retrieval system for Lean 4 to date. Precision on LogicBrain-style structured proof stores not yet tested. Trigger (>=80% precision on structured KB) still not met externally. |
| Gap 3 (Forgetting) | Trigger: >= 95% performance at >= 50% reduction | **Met** — Z3 compaction achieves 96–98% reduction with 100% conclusion preservation | Memanto (Apr 2026) and Temporal Memory paper (Apr 2026) show external field converging on information-theoretic agent memory. **Jul 2026:** Active Context Compression (arXiv 2601.07190) adds autonomous memory management (22.7% token reduction). LogicBrain trigger already met; dependency-aware pruning remains open. |
| Gap 4 (Strategy Transfer) | Trigger: verified transfer with formal guarantee | **Experimentally validated** — uniform substitution achieves 100% transfer rate (21/21 valid, 6/6 invalid preserved). See `tests/experiments/test_proof_template_transfer.py` | MA-LoT and REAL-Prover set new Lean4 benchmarks. **Jul 2026:** Lean4Agent (arXiv 2606.06523v2, Jun 15, 2026) introduces FormalAgentLib — first Lean 4 library for formal agent workflow verification; verifies structural/semantic/trajectory validity but not strategy applicability across tasks. Leanstral 1.5 (v26.06) released. MiniF2F approaching saturation (Kimina-Prover 92.2%). LogicBrain ProofTemplate still the only result with formal strategy-transfer guarantees. |

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
