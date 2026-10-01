# Stage 4 Research Watch

Last reviewed: 2026-10-01

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

| Project / Line of Research | Why it matters | Status (2026-10) |
|----------------------------|----------------|-------------------|
| Continual Learning with Elastic Weight Consolidation and successors | Prevents catastrophic forgetting in neural nets by penalizing changes to important weights | Active 2026: "EWC Done Right" (arxiv 2603.18596) **accepted to CVPR 2026** (Mar 2026); introduces Logits Reversal (LR) operation to fix Fisher Information estimation (gradient vanishing + inaccurate importance); significantly outperforms EWC variants. Hybrid architecture achieves 0.8% vs EWC's 2.3% degradation per task. No agent-level solution yet demonstrating >=100 diverse tasks. **Context Channel Capacity Framework** (arXiv 2603.07415, Mar 2026) formally proves the "Impossibility Triangle": zero forgetting, online learning, and finite parameters cannot simultaneously hold; defines C_ctx (context channel capacity) = mutual information between context signal and parameters; validates across 8 CL methods on Split-MNIST (1,130+ experiments), showing C_ctx perfectly predicts forgetting behavior. **Aug 2026:** Two companion Jun 2026 papers reframe the mechanistic nature of forgetting itself (see Accessibility Collapse row below). |
| DPO successors (Rafailov et al., 2023) and reward-model-free alignment | Reduces reward hacking by eliminating explicit reward models | Active 2026: **Gate-DPO** (arxiv 2605.02626, May 2026) addresses DPO's probability-collapse "squeezing effect" by gating rejected gradients based on the model's probability geometry; smaller gated models outperform larger ungated ones, suggesting gradient control > scale for stability. α-DPO, PAR remain active. Formal bounds on policy drift still absent. **POET** (arXiv 2506.09457, ACL 2026 Findings) addresses "reward-generation gap" in DPO/SimPO via prefix-oriented equal-length training; +11.8pp on AlpacaEval 2. **Confident Layer Decoding** (arXiv 2606.21906, Jun 20, 2026) mitigates alignment tax via entropy-guided backward layer search; gains on GPQA-Diamond, Omni-MATH, HLE with <2% latency increase and zero memory overhead. |
| GFlowNets (Bengio et al., 2021) | Diversity-preserving exploration that may resist mode collapse | Active 2026: **Goal2FlowNet** (OpenReview) uses GFlowNets to learn exploratory goal-conditioned policy covers, improving sample complexity and zero-shot generalisation for goal-conditioned RL. Integration in general agent learning loops still limited. **GFlowNet-OT** (arXiv 2606.06272, Jun 4, 2026, ICML 2026 SPIGM Workshop) establishes that non-acyclic GFlowNets solve optimal transport when configured as minimum-flow systems; minimum-flow GFlowNet objective reduces to Kantorovich OT problem with graph-induced shortest paths; enables large-scale graph OT via neural edge-flow parameterization. **PPO for GFlowNets** (arXiv 2606.15793, Jun 14, 2026) first derives and applies PPO to GFlowNets; improved convergence speed and data efficiency vs. standard GFlowNet objectives on synthetic energy functions and molecular graph generation. **Aug 2026:** **Stable-GFlowNet** (arXiv 2605.00553, ICML 2026 poster, Jun 30 final revision) applies GFlowNets to LLM red-teaming; eliminates partition function Z estimation via pairwise contrastive trajectory balance; adds fluency stabilizer to prevent local-optima collapse to gibberish; KAIST group, accepted to ICML 2026. Theoretical foundations now much stronger; agent-loop integration still limited. **Sep 2026:** **GFlowRL** (arXiv:2607.13394, Jul 2026) — extends GFlowNet-style distribution-matching RL to LLM reasoning; trajectory balance objective with learned partition function approximation; scales GFlowNet-style training to large LLMs. **Oct 2026 (Sep papers):** **FlowMAS** (arXiv:2609.37151, Sep 29, 2026) — GFlowNet-based multi-agent workflow topology learning for LLM agents; models workflow generation as reward-guided flow over the topology space; curiosity-driven module for novel-structure exploration; information-guided module evaluates information contribution and communication efficiency of operator choices; beats 15 baselines on multiple benchmarks with multiple LLM backbones. First application of GFlowNets to automated multi-agent LLM coordination. **A Theory of Multi-Agent Generative Flow Networks** (arXiv:2509.20408, Sep 2026) — theoretical foundations for multi-agent GFlowNets. Agent-loop integration for single-agent reasoning still limited. |
| RLHF stability guarantees (Constitutional AI lineage) | Formal bounds on policy drift during online learning | Active 2026: arxiv 2601.16403 (Jan 2026) — first formal analysis of KL-regularized RLHF. **"A Tighter Bound for Reward Learning in RLHF"** (ICLR 2026, OpenReview forum EyMoFzI3Oz) and **"Provably Efficient Online RLHF with One-Pass Reward Modeling"** (arxiv 2502.07193) published. Formal bounds on online policy *drift* remain open; bounds address reward learning and convergence, not drift across deployment. **Explaining and Preventing Alignment Collapse in Iterative RLHF** (arXiv 2605.04266, May 7, 2026; Bach, Jordan) — formal bounds (Theorems 2.1, 3.1–3.6) characterizing collapse conditions and convergence rates; influence-function-based prevention strategy for maintaining alignment stability. Closest yet to formal bounds on iterative policy drift; deployment drift across diverse tasks remains open. **Aug 2026:** **Meta-Learned Reward Shaping for RLHF** (arXiv 2607.26094, Jul 2026) — provides theoretical guarantees for policy invariance, analyzes representation drift sensitivity formally, and addresses incentive misalignment from entropy maximization; new closest result to formal deployment drift bounds. **Sep 2026:** **What Matters in Data for DPO?** (arXiv:2508.18312, Aug 2026) — empirically identifies chosen response quality as dominant DPO factor; online DPO reduces to SFT on chosen responses; contrastiveness between responses helps primarily via improving chosen samples. Practical dataset construction guidance; no new formal drift bounds. **Oct 2026 (Sep papers):** **FestDPO** (arXiv:2609.34673, Sep 28, 2026) — extends DPO to few-step generative implicit models via nonparametric likelihood estimation; asymptotically consistent sample-based approximation; agnostic to sampling procedure and model family; outperforms preference optimization baselines on text-to-image and protein backbone generation. Not specific to language model alignment or agent settings; no stability-at-scale results. **Inducing Emergent Misalignment from Reward Hacks with Iterative DPO** (arXiv:2609.06649, Sep 6, 2026) — studies how reward hacking during RL from verifiable rewards can induce broad misalignment; iterative DPO used to probe selective generalization from semi-online RL. No new formal drift bounds; reinforces instability concern. |
| LeanAgent (Anandkumar et al. / LeanDojo, 2023–2026) | Lifelong learning system for Lean 4 theorem proving — improves through experience across tasks | Active 2026: ICLR 2025 paper; **LeanProgress v3** (arxiv 2502.17925v3) code merged into LeanDojo-v2 (confirmed May 2026); 75.8% proof progress prediction accuracy (MAE 3.15 steps with history), +3.8pp on Mathlib4 proof search vs baseline of 41.4%. |
| **ProgAgent** (arxiv 2603.07784, Mar 2026) | Continual RL agent deriving dense shaped rewards from unlabeled expert videos; directly addresses catastrophic forgetting + reward specification cost | **New (2026-06)** — outperforms key baselines on ContinualBench and Meta-World; real-robot trials validate complex manipulation skill learning. Robotic domain only; no extension to general agent reasoning loops yet. |
| **Catastrophic Forgetting as Accessibility Collapse + Stable Recovery Manifold** (arXiv 2606.06032 + arXiv 2606.13637, Jun 4 + Jun 11, 2026) | Two companion papers that reframe forgetting as a geometric accessibility failure at the final readout layer, not destruction of representations — with direct implications for recovery-based CL methods | **New (2026-08)** — 2606.06032 (Trivedi & Melwani): task accuracy collapses from 54.8% to 0% on sequential CIFAR-100, but linear probe retains ~76% of representational information; proposes Accessibility Collapse Hypothesis. 2606.13637 (companion): introduces Stable Recovery Manifold (SRM) — forgotten knowledge preserved in compact ~8-direction subspace (constant across tasks, σ = 0.82); 82% of recoverability variance explained by 3 geometric variables; principal-angle drift is dominant predictor (Pearson r = -0.862). Together these papers identify *subspace orientation preservation* as the primary target for next-generation CL methods — more informative than EWC importance-weight framing. No agent-level solution yet. |
| **RL Forgets! Towards Continual Policy Optimization (CPO)** (arXiv:2607.04364, Jul 2026) | Continual RL post-training for vision-language models; identifies KL regularization mismatch — standard KL is evaluated on current-task data, not prior tasks — and proposes CPO, a replay-free framework grounding regularization in prior-task behavioral KL, converted to sparse parameter-movement regularization | **New (2026-09)** — 13.7% reduction in forgetting, 7.0% improvement in pretrained model capabilities on Qwen3-VL-8B; introduces MRCL benchmark for multi-domain continual RL. Challenges assumption that RL is inherently more resistant to forgetting than SFT. No demonstration at ≥100 diverse task scale. |
| **Geometry of Forgetting: Representation Flux in Continual Learning** (arXiv:2608.15854, Aug 2026) | Geometric companion to the Accessibility Collapse / Stable Recovery Manifold papers (arXiv:2606.06032 / 2606.13637); introduces "representation flux" — a sample-level measure of representation displacement across training — as an early-warning signal that predicts forgetting before accuracy drops | **New (2026-09)** — Representation flux is strongly associated with catastrophic forgetting across SplitMNIST, SplitFashionMNIST, SplitCIFAR10, SplitTinyImageNet; FlowLess-R regularization constrains replay representations relative to stored references, improving ER, DER++, ER-ACE baselines. Extends the static SRM subspace analysis to a dynamic metric; no agent-level demonstration. |
| **FiUni: Unifying Detection and Adaptation in Task-Free Continual Learning** (arXiv:2608.27070, Aug 2026) | Task-free CL for LLMs — no explicit task boundary supervision; infers batch-level task affiliations via K-FAC orthogonality patterns in Fisher information matrices; dynamically expands, reuses, or creates LoRA subspaces | **New (2026-09)** — Fewer trainable parameters than task-aware baselines; dynamically balances knowledge sharing and task isolation without task labels. Most parameter-efficient task-free CL approach to date for LLMs. No agent-level demonstration at ≥100 diverse task scale. |
| **Homeostatic Continual Learning** (arXiv:2609.13771, Sep 12, 2026) | Biologically-inspired continual learning method for agents operating in changing environments; detects outliers in environment data when agent output is anomalous and updates only relevant model components; proposes factorized world-model building via concept abstraction and feature mapping | **New (2026-10)** — Nokia Bell Labs France; 18 pages, 12 figures; enables agent to gradually complete its model-policy pair without catastrophic forgetting; proposes concept-to-intent mapping via feature representations. No formal retention-rate evaluation; no comparison at ≥100 task scale; mechanism is heuristic outlier detection, not formal verification. |

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

| Project / Line of Research | Why it matters | Status (2026-10) |
|----------------------------|----------------|-------------------|
| Voyager skill library (Wang et al., 2023) | Demonstrates compositional skill storage and retrieval in Minecraft | Published; retrieval is embedding-based, not verified. No new developments. |
| Generative Agents reflective memory (Park et al., 2023) | Relevance + recency + importance scoring for episodic memory | Published; no formal verification of retrieved memories. No new developments. |
| RAG with structured knowledge graphs | Combines retrieval with graph-structured knowledge | Active 2026: GraphRAG mainstream; "Hierarchical Planning + KG-RAG + Symbolic Validation" (OpenReview); **CRAMF** (arxiv 2508.06931, concept-driven retrieval-augmented mathematical formalization) enhances LLM autoformalization by retrieving formal definitions of core mathematical concepts. Formal proof store integration still unexplored. |
| Verified retrieval (formal IR) | Retrieval algorithms with provable recall guarantees | Early stage 2026: Verifiable PIR research active in crypto domain (SNARKs-based); FIRE iterative retrieval for fact-checking. Not yet applicable to general knowledge bases. |
| **REAL-Prover** (arxiv 2505.20613, Leansearch-PS) | Retrieval-augmented open-source Lean 4 prover; combines fine-tuned LM with Leansearch-PS retrieval component for college-level math | **New (2026-06)** — 23.7% on ProofNet (Pass@64); **56.7% on FATE-M algebraic benchmark (new SOTA)**. Retrieval is for premise/lemma lookup, not verified retrieval. Precision on structured proof stores not yet reported. |
| **LeanSearch v2** (arXiv 2605.13137, May 14, 2026) | Global premise retrieval for Lean 4 theorem proving; two-mode operation (standard + reasoning-aware); open-sourced code, data, and benchmarks | **New (2026-07)** — 46.1% recovery of ground-truth premise groups within 10 candidates on 69 research-level Mathlib4 theorems (vs. 38.0% reasoning-system baseline and 9.3% premise-selection baseline); integrated with fixed prover loop achieves 20% proof success vs. 16% with next-best system. Most capable open premise-retrieval system for Lean 4 to date; precision on structured proof stores not yet reported. |
| **OProver** (arXiv 2605.17283, May 17, 2026) | Unified agentic formal theorem proving framework that integrates agentic proving directly into prover training; builds OProofs — 1.77M Lean statements, 6.86M compiler-verified proofs, serialized retrieval-repair trajectories | **New (2026-08)** — OProver-32B achieves best Pass@32 on MiniF2F (93.3%), ProverBench (58.2%), PutnamBench (11.3%); ranks second on MathOlympiad (22.8%) and ProofNet (33.2%); more top placements than any prior open-weight whole-proof prover. Agentic loop: fails → retrieve compiler-verified proofs from OProofs → repair; repair traces used as SFT data; unresolved cases go to RL. Retrieval is from a verified proof corpus; no formal guarantee of applicability to new task yet. |
| **VERITAS** (arXiv 2606.19399, Jun 17, 2026) | Verifier-guided proof search that routes every Lean verifier signal (syntax errors, type mismatches, partial goal progress) back into search — not just pass/fail | **New (2026-08)** — Zero-shot; reaches 40.6% on miniF2F (vs. Best-of-5 baseline 36.9%, Portfolio 26.2%); releases VERITAS-CombiBench (55 combinatorics theorems). Protocol: Best-of-N Phase 1 → critic-guided MCTS Phase 2 ingesting Phase 1 failures as explicit negative examples; preserves every theorem solved by Phase 1. Complementary to LeanSearch: VERITAS exploits verifier feedback signal; LeanSearch exploits premise structure. |
| **ArXivLean** (MathArena, 2026) | Open benchmark of 41 research-level Lean theorems from arXiv March 2026 papers; intended to replace saturated miniF2F as difficulty frontier | **New (2026-08)** — All tested models, including Harmonic's Aristotle agent, scored below 20% with full tool access (Lean verification, semantic Mathlib search, persistent lemma file). Signals that miniF2F saturation (see Gap 4) does not transfer to genuine research-level difficulty. Refreshed regularly to minimize contamination. |
| **MathForm** (arXiv:2608.14221, Aug 2026) | Knowledge retrieval + verification-guided iterative refinement for Lean 4 mathematical autoformalization; builds FormalVerse — ~367K verified Lean 4 examples across diverse mathematical domains; retrieves relevant Mathlib definitions before generation, then iteratively revises using Lean compiler diagnostics | **New (2026-09)** — MathForm-8B achieves 88.06% Pass@8 (syntax check), 72.37% Pass@8 (consistency check); 63% / 37% on FATE-H / FATE-X; outperforms 32B specialized baselines. Retrieval is from a 26K+ Mathlib concept-definition knowledge base, not a CertificateStore-style verified proof store. Iterative Lean compiler feedback loop is structurally analogous to LogicBrain's query_consistent + compact loop. Precision on structured arbitrary-domain proof stores not yet reported. |
| **PAGR: Proof-Carrying Algebraic-Geometric Retrieval** (arXiv:2609.06127, Sep 5, 2026) | Formally grounded RAG framework that separates three conflated questions in knowledge-base retrieval: what is certified as knowledge, what representations aid retrieval, and what multi-hop compositions are admissible; uses typed quiver + provenance + sheaf theory; certification is reserved exclusively for source-attested base facts and their Horn-rule logical consequences — learned components may only rank/propose, never certify | **New (2026-10)** — Four-layer architecture: symbolic layer (typed quiver + Horn inclusions), algebraic representation (linear operators for relation types), geometric layer (metric representation spaces), provenance/sheaf layer (evidence traceability). Most formally grounded verified retrieval framework for RAG to date. Separates ranking from certification in a way directly analogous to LogicBrain's Z3 consistency checker as a certification oracle. No empirical evaluation on structured proof stores yet reported; theoretical framework only. |

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

| Project / Line of Research | Why it matters | Status (2026-10) |
|----------------------------|----------------|-------------------|
| Memory consolidation in cognitive architectures (SOAR, ACT-R) | Decades of research on selective forgetting in symbolic systems | Mature theory; limited integration with modern agents. No new 2026 developments. |
| Compression-based forgetting (information-theoretic) | Discard knowledge that is redundant given remaining knowledge | **Active 2026**: **Memanto** (arxiv 2604.22085, Apr 2026) — typed semantic memory with 13-category schema, automated conflict resolution, temporal versioning, information-theoretic search (no indexing); 89.8% on LongMemEval, 87.1% on LoCoMo, new SOTA. **Temporal Memory for Resource-Constrained Agents** (arxiv 2604.00067, Apr 2026) — stochastic compress-add-smooth framework for continual learning under memory budget. **Memory Bank Compression for CL in LLMs** (arxiv 2601.00756, Jan 2026) — codebook-based compression of memory banks. First concrete agent implementations with IT compression now published. |
| Schema evolution / knowledge compaction | Merge multiple specific proofs into generalized rules | Active in database community; unexplored for proof stores. No 2026 bridge work found. |
| **Active Context Compression / Focus Agent** (arXiv 2601.07190, Jan 2026) | Autonomous memory management in LLM agents; "Focus Agent" consolidates learnings into persistent Knowledge blocks without human intervention | Early 2026: 22.7% average token reduction while maintaining task accuracy; up to 57% token savings on individual instances; averages 6.0 autonomous compressions per task. Complements information-theoretic approaches (Memanto); not yet applied to proof stores. |
| **Memanto** (arxiv 2604.22085, Apr 2026) | Universal typed semantic memory for long-horizon agents; automated conflict resolution + temporal versioning + information-theoretic retrieval (no separate vector index required) | **New (2026-06)** — SOTA on LongMemEval (89.8%) and LoCoMo (87.1%), surpassing graph+vector hybrids with a single retrieval query and zero ingestion cost. Architecture is analogous to what a LogicBrain-backed store would need for agent-facing retrieval; conflict resolution maps directly to Z3 consistency checking. |
| **OSL-MR** (arXiv 2606.10616, Jun 2026) | Observability-safe memory retention via constrained stochastic optimization; formalizes retention as a multi-step NP-hard optimization with budget feasibility, evidence utility, and delayed miss/reacquisition/stale penalties | **New (2026-08)** — Proposes OSL-MR (Observability-Safe Learning for Memory Retention): enforces strict separation between online-observable features and offline-available supervision; combines evidence learner with Mixed-Score heuristic. Outperforms recency-based, Generative Agents-style, and other heuristic baselines on LoCoMo and LongMemEval under tight budgets. First formal NP-hardness proof for memory retention scheduling. Complementary to LogicBrain compact() in that it addresses when to retain, not what to merge. |
| **Retain or Consolidate?** (arXiv 2607.17545, Jul 20, 2026) | Budget-dependent operator selection for language agent memory: formalizes the decision between retaining raw records vs. consolidating (Merge / Abstract / Rewrite), decomposing each operator's utility into coverage effect and signed replacement effect | **New (2026-08)** — Provides the first formal decomposition of retain-vs-consolidate trade-off as a function of memory budget and evidence redundancy. Directly applicable to LogicBrain certificate store evolution: when budget is tight, compact(); when budget allows, retain raw certificates for audit. |
| **Rate-Distortion View of Memory Compaction** (arXiv 2607.08032, Jul 9, 2026) | Unified rate-distortion framework covering KV-cache eviction, prompt pruning, recurrent state bounding, and agent memory consolidation; single compaction objective + layer-agnostic lower bound; seven-axis taxonomy | **New (2026-08)** — Argues all memory compaction decisions across LLM layers are instances of the same rate-distortion problem. Provides principled lower bounds on information loss. Relevant to LogicBrain: provides theoretical grounding for compact() and future dependency-aware pruning policies. |
| **Memory as a Controlled Process** (arXiv 2607.13591, Jul 2026) | Learned adaptive memory management for LLM agents; treats store/retrieve/update/summarize/discard as RL-optimized tools | **New (2026-08)** — Agents learn to proactively summarize intermediate results before context fills up and selectively discard semantically similar records; optimized with reinforcement learning. Complementary to OSL-MR (rule-based optimization) vs. RL-based policy. |
| **FSFM: Biologically-Inspired Framework for Selective Forgetting of Agent Memory** (arXiv:2604.20300, Apr 2026) | Biologically-inspired agent memory pruning framework (hippocampal indexing, Ebbinghaus forgetting curve); addresses efficiency (intelligent pruning), quality (outdated preference removal), and security (active forgetting of malicious / sensitive / privacy-compromising content); four forgetting modes: passive decay, active deletion, safety-triggered, adaptive reinforcement | **New (2026-09)** — +8.49% access efficiency, +29.2% signal-to-noise ratio, 100% elimination of security risks, 30% storage reduction, 1.3× faster query processing. Missed in prior (Aug 2026) review cycle. Not yet applied to proof stores; security-triggered forgetting maps to LogicBrain contradiction rejection. |
| **SF-AMS: Strategic Forgetting for Structured Memory in LLM Agent** (arXiv:2607.22562, Jul 2026) | Dynamic utility-driven memory management; replaces static decay rates with long-term importance modeling based on actual usage patterns and temporal signals; composite importance scoring at semantic + entity levels; hierarchical structure preserving entity-consistent information | **New (2026-09)** — +9.65 F1 multi-hop reasoning (Qwen2.5-7B), +6.91 temporal reasoning (GPT-4o-mini), +6.53 open-domain; generalizes across architectures. Extends OSL-MR (rule-based retention optimization) and "Retain or Consolidate?" (formal trade-off decomposition) with empirically learned importance signals. |
| **Control-Plane Placement Shapes Forgetting** (arXiv:2606.15903, Jun 2026) | Architectural study of 13 agent memory system configurations; ForgetEval benchmark — 1,000 templated + 385 adversarial test cases; diagnoses deletion/update failures ("forgetting") as distinct from recall failures; production failures are predominantly forgetting, not recall | **New (2026-09)** — Mutation-time LLM hook achieves 91.7–93.2% accuracy including intent-aware deletion (78–85%); deterministic primitives only 5% on canonicalization tasks; LLM-at-inscription achieves perfect canonicalization but cannot handle intent-aware deletion. Directly applicable to LogicBrain: Z3 verifier can act as a deterministic mutation-time check, compensating for the known weakness of pure deterministic architectures. MIT-licensed ForgetEval released. |
| **Why Does CLAUDE.md Keep Growing? Catastrophic Remembering in Agentic Coding** (arXiv:2608.11095, Aug 2026) | Empirical study of instruction-prompt accumulation in 1,867 agentic coding repositories; identifies "catastrophic remembering" as the inverse of catastrophic forgetting — asymmetric deletion cost causes unbounded prompt growth (+226% over instruction lifetime, +4.9 net instructions per commit); older instructions resist deletion (log-hazard −0.032/commit) | **New (2026-09)** — Prompt comments encoding latent reasoning reduce excess instructions by 99.3% in controlled settings (+211% → +1.4%); +23.1% real-world instruction-following improvement. Directly relevant to LogicBrain: certificate accumulation without periodic compaction mirrors this phenomenon; `CertificateStore.compact()` is the formal analogue of the proposed prompt-comment strategy, and staleness-aware pruning would address the deletion-resistance asymmetry. |
| **The Compaction Cliff in Long-Running AI Agent Memory** (arXiv:2608.22752, Aug 2026) | Identifies the "compaction cliff" — a threshold at which gradual context growth triggers a sudden, severe quality collapse in long-running agent tasks; characterizes when and why naive summarization-based compaction fails | **New (2026-10, missed in Aug review)** — Empirically identifies that memory compaction failures are cliff-shaped, not smooth; frequent small compactions outperform rare large ones. Directly relevant to LogicBrain: `CertificateStore.compact()` mitigates this by compacting eagerly via Z3 entailment rather than summarization; periodic compaction scheduling is better than deferred batch compaction. |
| **Compact-Memory LLM Agents via Online Max-Member Clustering and Atom-Aware Packing** (arXiv:2609.04915, Sep 2026) | Addresses quality–token trade-off in compact-memory LLM agents; proposes RSM-full — an online clustered-memory pipeline combining cosine-gated max-member merge write rule and atom-aware grouped context packer | **New (2026-10)** — 83% of full-context quality at 32% of token cost on AMA-Bench; beats closest streaming-clustered baseline (Online K-Means) by +3.5–6.0pp; reproduces on RealMem benchmark. Complementary to Rate-Distortion View and OSL-MR: addresses the practical write/merge side of compaction rather than the retention-scheduling side. Not applied to proof stores. |
| **ReCAP: Persistent Context Graphs for Efficient Memory Compaction in LLM Agents** (arXiv:2609.40118, Sep 30, 2026) | Stores attention-derived importance scores and dependency links in a lightweight, persistent context graph; combines stored importance with request-level relevance cues and dependency-link following for message selection, without additional model calls | **New (2026-10)** — 95% latency reduction for compaction and cold restoration on both Qwen3-Coder and gpt-oss; halves historical context per call on SWE-Together at comparable task quality; +19.8 and +41.2 accuracy points on code tasks. Most practical deployed-agent compaction result to date. Dependency-link tracking maps directly to LogicBrain's need for dependency-aware pruning in `CertificateStore`: never prune a certificate that others depend on. Code available at github.com/UCSB-NLP-Chang/ReCAP. |

**Trigger condition for LogicBrain work:**
A demonstrated forgetting policy maintaining >= 95% task performance
while reducing stored knowledge by >= 50% would warrant extending
CertificateStore with verified pruning.

**What LogicBrain has built (2026-03-22):**
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

| Project / Line of Research | Why it matters | Status (2026-10) |
|----------------------------|----------------|-------------------|
| Voyager (Wang et al., 2023) | Skill library with compositional reuse | Published; skills are code snippets, not verified. No new developments. |
| Program synthesis for strategy abstraction | Abstract specific solutions into reusable templates | No 2026 DreamCoder/LAPS successors found. LILO (ICLR 2024) — library learning via compression + LLM documentation — remains most recent practical successor; no 2026 update. Open problem. **Aug 2026:** **DreamProver** (see below) is the closest theorem-proving analogue of DreamCoder's wake-sleep library learning. **TheoryCoder-2** (see below) demonstrates active abstraction learning in program-synthesis agents. |
| Analogical reasoning in LLMs | LLMs can draw structural analogies | Capability exists but is unreliable and unverified. No new 2026 results. |
| Proof-strategy libraries (Isabelle, Lean tactics) | Formal proof assistants already have tactic libraries | Mature; but human-curated, not learned. |
| **Leanstral** (Mistral AI, 2026-03 → 2026-06) | First open-source LLM agent specifically trained on Lean 4 repositories; 6B params (119B total, MoE), Apache 2.0, MCP-compatible; learns to apply tactics across real-world Lean codebases | Active 2026: pass@2 = 26.3 (v26.03), beats Claude Sonnet 3.7 by 2.6 points at ~1/15 the cost ($36 vs $549). **Aug 2026 update:** **Leanstral 1.5 (v26.06) released June 30, 2026** — **saturates miniF2F completely (100% on both val and test)**; solves 587/672 PutnamBench problems; FATE-H 87%, FATE-X 34%; FLTEval pass@1 28.9 / pass@8 43.2 (surpasses Opus 4.6's 39.6 at 1/7th the cost); **discovers 5 previously unknown bugs across 57 real Lean repositories**. Apache 2.0 license, MCP support maintained. Still no verified strategy-transfer guarantee. **Sep 2026:** Leanstral 1.5 hosted API retired Sep 30, 2026; Apache 2.0 open weights remain available. No Leanstral 2.0 release announced as of Oct 2026. |
| LeanCopilot / LeanDojo (Anandkumar Lab, 2023–2026) | Retrieval-augmented LLM proof assistant; LeanDojo provides structured access to Lean repos for training and inference | Active 2026: **LeanDojo-v2 released April 26, 2026** — end-to-end framework combining repository tracing, lifelong dataset management, retrieval-augmented agents, Hugging Face fine-tuning, and external inference APIs; **LeanProgress v3** (arxiv 2502.17925v3) code merged into LeanDojo-v2 (confirmed May 2026); 75.8% proof progress prediction accuracy, +3.8pp on Mathlib4 search (from 41.4% baseline). **Sep 2026:** **LeanCopilot v4.34.0** released Sep 18, 2026 — routine Lean v4.34.0 version bump; active maintenance continues. |
| **MA-LoT** (arxiv 2503.03205, Mar 2025 / v3 May 2025) | Multi-agent Lean 4 prover using long chain-of-thought; separates proof generation from error-analysis via multi-LLM collaboration; LoT-Transfer Learning avoids need for annotated data | **New (2026-06)** — 61.07% on MiniF2F-Test (Lean 4), outperforming DeepSeek-V3 (33.61%), InternLM-Step-Prover (50.70%), and Godel-Prover (55.33%). Strategies are LLM-generated, not verified. Relevant as a benchmark baseline for Leanstral / LeanCopilot comparisons. |
| **Lean4Agent** (arXiv 2606.06523v2, Jun 15, 2026) | First comprehensive framework applying Lean 4 dependent-type formal language to LLM agent behavior verification; introduces **FormalAgentLib** — extensible Lean 4 library for formally modeling and verifying agent workflows and trajectories via three-layer verification (structural, semantic, trajectory) | **New (2026-07)** — workflows passing semantic verification outperformed failing ones by **14.80%** on software engineering tasks and **9.07%** on paper understanding tasks; LeanEvolve refinement method adds 7.47% average improvement on engineering problems. Direct relevance to LogicBrain: FormalAgentLib is the first Lean 4 substrate for agent workflow verification analogous to what Stage 4 would require. Verifies workflow structure and trajectory validity, not strategy applicability; no verified strategy-transfer guarantee yet. |
| **MiniF2F SOTA cluster** (2026) | Kimina-Prover 92.2%, Goedel-Prover-V2 90.4%, DeepSeek-Prover-V2 88.9% on MiniF2F; machine-verified Fermat-Goldbach–Gutmann quantum conjecture (arXiv 2606.29687, Jun 2026) using Claude AI + Lean 4 demonstrates frontier AI discovering and machine-verifying novel research-level proofs | **Aug 2026 update:** **miniF2F is now fully saturated** — Leanstral 1.5 reaches 100%, OProver-32B reaches 93.3% Pass@32. Community benchmark focus shifted to research-level difficulty: ArXivLean (all models <20%), ProverBench, PutnamBench, FATE-H/X, and FLTEval. All systems generate LLM-produced tactics; none provide verified strategy-transfer guarantees. |
| **DreamProver** (arXiv 2604.26311, Apr 29, 2026) | Theorem-proving agent that evolves transferable lemma libraries via iterative wake-sleep cycles — directly analogous to DreamCoder's program synthesis approach applied to formal proofs | **New (2026-08)** — Wake phase: proves training theorems, proposes new candidate lemmas. Sleep phase: abstracts, refines, and consolidates candidates to compress and optimize the library. Result: compact set of high-level transferable lemmas improving proof success on unseen theorems in related domains; also produces more concise proofs and reduces computational cost. Most direct DreamCoder-lineage work for formal theorem proving. Lemmas are abstracted but not machine-verified as applicable to new tasks; transfer guarantee is empirical, not formal. |
| **CircuitProver** (arXiv 2607.27259, Jul 29, 2026) | Agentic Lean 4 framework for hardware verification that builds reusable circuit proof libraries; verified lemmas and proof strategies are distilled and reused across related hardware verification tasks | **New (2026-08)** — Translates parameterized hardware designs + natural-language specs into Lean 4 models; iteratively constructs machine-checked proofs via Lean feedback; distills proving traces into reusable libraries where proving strategies guide future agent reasoning and verified lemmas support proof reuse. Addresses the "repeatedly reconstructed" problem in hardware verification. Closest existing result to verified strategy-transfer in a constrained domain: Lean's type-checker provides a formal guarantee that reused lemmas are applicable. Domain restricted to hardware circuit verification. |
| **TheoryCoder-2** (arXiv 2602.00929, ICLR 2026) | Theory-Based RL agent that actively learns reusable abstractions by synthesizing them from experience; integrates abstractions into hierarchical planning; significantly more sample-efficient than baseline LLM agents | **New (2026-08)** — Experiments on BabyAI, Minihack, VGDL (Sokoban); solves complex tasks where baselines fail while requiring minimal human prompts; outperforms WorldCoder and other prior program-synthesis agents in sample efficiency. Abstractions are LLM-synthesized Python programs, not verified; no formal guarantee of transfer correctness. Relevant as a successor to DreamCoder/LAPS for agent-level abstraction learning. |

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

| Gap | Before Experiments | After Experiments | 2026-10 Update |
|-----|-------------------|-------------------|----------------|
| Gap 1 (Stable Learning) | Trigger: external breakthrough needed | Unchanged — still requires external breakthrough | Gate-DPO (May 2026) improves DPO stability; EWC Done Right (CVPR 2026); ProgAgent shows continual RL progress. **Aug 2026:** Two new companion papers reframe forgetting mechanistically: Accessibility Collapse (arXiv 2606.06032) shows task accuracy → 0% while representations retain ~76% of information; Stable Recovery Manifold (arXiv 2606.13637) shows forgotten knowledge lives in a stable ~8-direction subspace — subspace orientation is the key preservation target, not importance weights. Meta-Learned Reward Shaping for RLHF (arXiv 2607.26094, Jul 2026) adds formal policy invariance and drift sensitivity bounds — new closest result to deployment drift guarantees. Stable-GFlowNet (ICML 2026) advances GFlowNet stability. Trigger (>=100 diverse tasks, no reward hacking, no drift) still not met. **Sep 2026:** Geometry of Forgetting (arXiv:2608.15854) extends geometric forgetting analysis with representation flux — dynamic early-warning signal; FlowLess-R regularization improves replay baselines. FiUni (arXiv:2608.27070) achieves task-free CL for LLMs via K-FAC orthogonality + LoRA, no task-boundary supervision needed. RL Forgets! CPO (arXiv:2607.04364) reduces policy forgetting 13.7% in continual VLM post-training; introduces MRCL benchmark. GFlowRL (arXiv:2607.13394) scales GFlowNet distribution-matching RL to large LLMs. What Matters in Data for DPO? (arXiv:2508.18312): chosen-response quality dominant, online DPO ≈ SFT on chosen — practical data guidance, no new formal drift bounds. **Oct 2026 (Sep papers):** Homeostatic Continual Learning (arXiv:2609.13771) proposes biologically-inspired outlier-driven CL for agents; concept factorization for world-model building; no formal retention rates. FestDPO (arXiv:2609.34673) extends DPO to implicit generative models; no language model stability results. Inducing Emergent Misalignment from Reward Hacks with Iterative DPO (arXiv:2609.06649) shows iterative DPO reward hacking induces broad misalignment — reinforces stability concern. FlowMAS (arXiv:2609.37151) applies GFlowNets to multi-agent LLM workflow topology learning — first GFlowNet application to automated agent coordination. Trigger (≥100 diverse tasks, no reward hacking, no drift) still not met. |
| Gap 2 (Retrieval) | Trigger: >= 80% precision on structured KB | **Partially met** — Z3 consistency filter achieves this for propositional logic; needs testing on diverse/multi-domain KBs | REAL-Prover and CRAMF advance retrieval-augmented Lean proving. LeanSearch v2 best open structured-retrieval system. **Aug 2026:** OProver (arXiv 2605.17283) integrates retrieval of compiler-verified proofs into an agentic training loop (OProofs: 1.77M statements, 6.86M proofs) — largest verified-proof retrieval corpus to date. VERITAS (arXiv 2606.19399) uses rich Lean verifier signals (not just pass/fail) for zero-shot proof search; 40.6% on miniF2F. ArXivLean benchmark shows all models below 20% on research-level theorems — retrieval precision gap at research-level difficulty is large and open. Trigger (>=80% precision on structured KB) still not met externally. **Sep 2026:** MathForm (arXiv:2608.14221) adds knowledge retrieval (26K+ Mathlib definitions) + iterative Lean compiler feedback for autoformalization; MathForm-8B outperforms 32B baselines (88.06% Pass@8 syntax, 72.37% consistency). Structurally closest to a retrieval+verification loop for a formal math store. Precision on an arbitrary-domain CertificateStore-style KB not yet reported; trigger still not met externally. **Oct 2026 (Sep papers):** PAGR (arXiv:2609.06127) introduces the most formally grounded framework to date for proof-carrying RAG — separates certification (source-attested facts + Horn consequences only) from ranking (learned components); typed quiver + sheaf theory; directly analogous to LogicBrain's Z3 checker as a certification oracle. Theoretical only; no empirical evaluation on structured proof stores yet. LeanCopilot v4.34.0 released Sep 18 (routine Lean version bump). Trigger (≥80% precision on structured KB) still not met externally. |
| Gap 3 (Forgetting) | Trigger: >= 95% performance at >= 50% reduction | **Met** — Z3 compaction achieves 96–98% reduction with 100% conclusion preservation | Memanto (Apr 2026) and Temporal Memory paper (Apr 2026) show external field converging on information-theoretic agent memory. Active Context Compression (arXiv 2601.07190) adds autonomous memory management (22.7% token reduction). **Aug 2026:** Four new papers advance principled forgetting policies: OSL-MR (arXiv 2606.10616) formalizes retention as NP-hard constrained optimization; "Retain or Consolidate?" (arXiv 2607.17545, Jul) decomposes retain-vs-compact decision formally; Rate-Distortion View (arXiv 2607.08032, Jul 9) unifies all compaction decisions under one framework; Memory as Controlled Process (arXiv 2607.13591, Jul) applies RL to memory operator selection. LogicBrain trigger already met; dependency-aware pruning and formal budget-aware compaction scheduling remain open. **Sep 2026:** FSFM (arXiv:2604.20300, Apr 2026, missed in prior review) provides biologically-inspired selective forgetting with 30% storage reduction, +29.2% SNR, 100% security risk elimination; security-triggered forgetting mode maps to LogicBrain contradiction rejection. SF-AMS (arXiv:2607.22562, Jul) adds dynamic utility-driven importance scoring (+9.65 F1 multi-hop). Control-Plane Placement (arXiv:2606.15903) shows mutation-time LLM hook achieves 91.7% accuracy on intent-aware deletion — production systems fail on deletion, not recall; Z3-at-mutation-time is a natural LogicBrain design point. Catastrophic Remembering (arXiv:2608.11095, Aug) documents +226% instruction growth in agentic coding repos — inverse of what compact() solves, reinforcing the importance of active compaction policies. Trigger met; dependency-aware pruning and staleness-aware scheduling remain open. **Oct 2026 (Sep papers):** Compaction Cliff (arXiv:2608.22752, Aug, missed) shows sudden quality collapse from gradual context growth — cliff-shaped failure, not smooth degradation; frequent small compactions win over rare large ones. Compact-Memory LLM Agents / RSM-full (arXiv:2609.04915) achieves 83% full-context quality at 32% token cost via online clustering + atom-aware packing. ReCAP / Persistent Context Graphs (arXiv:2609.40118, Sep 30) stores attention-derived importance + dependency links in persistent graph; 95% latency reduction; dependency-link tracking is the external analogue of LogicBrain's open dependency-aware pruning requirement. Trigger already met; dependency-aware pruning and staleness-aware scheduling remain open — ReCAP provides a practical template. |
| Gap 4 (Strategy Transfer) | Trigger: verified transfer with formal guarantee | **Experimentally validated** — uniform substitution achieves 100% transfer rate (21/21 valid, 6/6 invalid preserved). See `tests/experiments/test_proof_template_transfer.py` | MA-LoT and REAL-Prover set new Lean4 benchmarks. Lean4Agent (arXiv 2606.06523v2, Jun 2026) introduces FormalAgentLib. **Aug 2026:** miniF2F now fully saturated (Leanstral 1.5: 100%; OProver-32B: 93.3% Pass@32). DreamProver (arXiv 2604.26311) is the first DreamCoder-lineage wake-sleep approach applied to formal theorem proving — empirical lemma transfer, no formal guarantee. CircuitProver (arXiv 2607.27259, Jul 29) is the closest existing result to verified strategy-transfer: Lean-checked lemma reuse across hardware verification tasks with type-system applicability guarantee, but restricted to hardware circuits. TheoryCoder-2 (ICLR 2026) demonstrates active abstraction synthesis in program-synthesis agents. LogicBrain ProofTemplate remains the only result with a fully general formal strategy-transfer guarantee via Z3-checked instantiation. **Sep 2026:** No verified strategy-transfer breakthrough found in August 2026. No new DreamCoder-lineage program synthesis work identified. CircuitProver and DreamProver remain frontiers. LogicBrain ProofTemplate status unchanged. **Oct 2026 (Sep papers):** No verified strategy-transfer breakthrough in Sep 2026. No new DreamCoder/LAPS successor identified. FlowMAS (arXiv:2609.37151) applies GFlowNets to multi-agent topology generation, not single-agent strategy abstraction. CircuitProver and DreamProver remain the closest external results. LogicBrain ProofTemplate remains the only general formal strategy-transfer guarantee via Z3-checked instantiation. |

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
