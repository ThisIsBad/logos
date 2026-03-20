# Session Handoff

Last updated: 2026-03-20

## Last Completed Work

Latest completed implementation work in the repository:

- Added `logic_brain/adversarial_harness.py` with deterministic self-play episodes, contradiction/stale-proof/policy-bypass attacks, defensive scoring, and regression-ready report artifacts.
- Added adversarial harness coverage in `tests/test_adversarial_harness.py`, including fixed-seed reproducibility and stable campaign scoring.
- Added `logic_brain/verified_runtime.py` with a deterministic runtime phase machine that composes planning, contract checks, uncertainty enforcement, proof-carrying execution, recovery, and replayable event traces.
- Added runtime coverage in `tests/test_verified_runtime.py`, including successful closed-loop execution, replay stability, recovery-path handling, long-horizon multi-step execution, and an adversarial policy-block case.
- Added `logic_brain/trust_ledger.py` with explicit `TrustPolicy`, `FederatedProofLedger`, revocation/expiry handling, and queryable acceptance diagnostics for cross-domain proof reuse.
- Added federated-ledger coverage in `tests/test_trust_ledger.py` and `tests/test_metamorphic_trust_ledger.py`, including trust-policy reorder invariance.
- Added `logic_brain/recovery.py` with unified failure taxonomy, deterministic recovery protocol selection, retry-loop guards, and auditable recovery certificates.
- Added recovery classification hooks for execution-bus, orchestrator, planner, and goal-contract failures plus coverage in `tests/test_recovery.py` and `tests/test_metamorphic_recovery.py`.
- Added cost-risk-utility branch ranking to `logic_brain/counterfactual.py` with explicit `UtilityModel`, hard `SafetyBound` caps, and explainable `RankedBranch` outputs.
- Added ranking and metamorphic coverage in `tests/test_counterfactual.py` and `tests/test_metamorphic_counterfactual.py` so planner replay and affine utility scaling preserve expected order.
- Cleaned repo hygiene around MCP/client artifacts: removed obsolete `.claude/mcp.json`, archived `docs/implementation_brief_v07_mcp.md`, and updated `.gitignore` for local scratch/config files.
- Updated `docs/mcp_smoke_test_results.md` so the setup section reflects `.mcp.json` as the active Claude Code project config.
- Added `logic_brain/execution_bus.py` with proof-carrying action envelopes, certified precondition checks, postcondition validation, action traces, rollback recommendations, and proof-bundle compatibility.
- Added the `proof_carrying_action` MCP tool in `logic_brain/mcp_tools.py` and `logic_brain/mcp_server.py`.
- Added execution-bus tests in `tests/test_execution_bus.py`, `tests/test_mcp_action_bus.py`, `tests/test_metamorphic_execution_bus.py`, and extended MCP server coverage in `tests/test_mcp_server.py`.
- Fixed CI portability issues by aligning optional MCP typing handling, adding required dev dependencies in `pyproject.toml`, and including the `examples` package in editable installs.

Recent commits:

- `f31bf89` - "Add deterministic adversarial self-play harness (closes #45)"
- `2c2df82` - "Update roadmap and handoff after closing #48"
- `d5b6afb` - "Add closed-loop verified agent runtime (closes #48)"
- `8c2ce50` - "Update roadmap and handoff after closing #49"
- `4f4f89d` - "Add federated trust-domain proof ledger (closes #49)"

Latest local validation seen in this session:

- `python -m pytest -q tests/test_adversarial_harness.py` -> `5 passed`
- `python -m pytest -q tests/test_verified_runtime.py` -> `6 passed`
- `python -m pytest -q tests/test_trust_ledger.py tests/test_metamorphic_trust_ledger.py` -> `6 passed`
- `python -m pytest -q tests/test_recovery.py tests/test_metamorphic_recovery.py` -> `10 passed`
- `python -m pytest -q tests/test_counterfactual.py tests/test_metamorphic_counterfactual.py` -> `15 passed`
- `python -m pytest -q tests/test_integration_full_loop.py tests/test_mcp_server.py` -> `4 passed`
- `python -m pytest -q` -> `459 passed`
- `python -m ruff check logic_brain tests tools` -> clean
- `python -m mypy --strict logic_brain` -> clean
- `python -m pytest --cov=logic_brain --cov-report=term-missing --cov-fail-under=85` -> `89.63%`
- `python -m pytest -q -m metamorphic` -> `54 passed`
- GitHub Actions CI run `23358610033` on `main` -> green

## Current WIP

- No implementation issue is currently in progress.
- Local uncommitted docs sync exists in this handoff file only.

## Issue Queue

Open issues visible in GitHub now:

- No open vision issues remain from the current queue.

Queue assessment:

- There is still no concrete next implementation issue broken out beneath the remaining vision issues.
- `#43` is closed and its core acceptance criteria are now covered by the execution-bus code, MCP integration, metamorphic tests, and green CI.
- `#47` is closed: transparent branch scoring, hard safety dominance, deterministic replay-compatible ranking, and affine-scaling metamorphic coverage are implemented in the planner core.
- `#50` is closed: failure taxonomy unification, deterministic allowed protocols, retry guards, auditable recovery certificates, and metamorphic coverage are implemented.
- `#49` is closed: explicit trust-policy enforcement, deterministic revocation/expiry blocking, machine-readable cross-domain diagnostics, and policy-order metamorphic coverage are implemented.
- `#48` is closed: the repo now contains a replayable runtime state machine with integrated planning, contract, uncertainty, execution, recovery gates, long-horizon sequence coverage, and an adversarial policy-block scenario.
- `#45` is closed: the repo now contains reproducible adversarial episodes, contradiction/stale-proof/policy-bypass templates, explainable defensive scoring, and regression-ready campaign artifacts.
- The current queue from the active AGI-roadmap issue set is empty; the next step is to define the next wave of issues or benchmark expansions.

Recommended next step:

- Open the next concrete issue batch, likely around benchmark expansion, persisted runtime artifacts, or richer trust/recovery integrations.

## MCP Status

- **Claude Code:** uses `.mcp.json` in the project root
- **OpenCode:** uses `.opencode.json` in the project root
- **AntiGravity:** uses `~/.gemini/antigravity/mcp_config.json`
- **Server transport:** stdio with newline-delimited JSON-RPC
- **Exposed tools:** `verify_argument`, `certify_claim`, `check_assumptions`, `check_beliefs`, `counterfactual_branch`, `z3_check`, `check_contract`, `check_policy`, `z3_session`, `orchestrate_proof`, `proof_carrying_action`

## Important Notes

- Do not use `.claude/mcp.json` for Claude Code v2.1+; it is ignored.
- AntiGravity stores MCP config outside the repo, so that setup cannot be fully checked in.
- `.gitignore` now suppresses common local scratch/config files such as `AGENTS.md`, `CLAUDE.md`, `architektur-stefano.md`, `claude_mcp_debug.log`, `docs/gemini_review_prompt_de.md`, `nul`, and `.claude/`.

## Process Rules

- Treat `docs/agi_roadmap_v2.md` as the primary AGI framing document and `docs/logicbrain_development_roadmap.md` as the actionable LogicBrain roadmap.
- Read `docs/development_process.md` for the canonical workflow.
- One issue at a time, with full preflight gates before each implementation commit.
- Keep `docs/new_session_handoff.md` current after each completed issue, at WIP changes, and when queue or blocker state materially changes.
- If implementing a new issue: run pytest, ruff, mypy strict, coverage gate, and metamorphic tests before commit.
- Commit and push autonomously once gates pass.
