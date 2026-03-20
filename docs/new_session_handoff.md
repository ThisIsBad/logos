# Session Handoff

Last updated: 2026-03-20

## Last Completed Work

Latest completed implementation work in the repository:

- Added cost-risk-utility branch ranking to `logic_brain/counterfactual.py` with explicit `UtilityModel`, hard `SafetyBound` caps, and explainable `RankedBranch` outputs.
- Added ranking and metamorphic coverage in `tests/test_counterfactual.py` and `tests/test_metamorphic_counterfactual.py` so planner replay and affine utility scaling preserve expected order.
- Cleaned repo hygiene around MCP/client artifacts: removed obsolete `.claude/mcp.json`, archived `docs/implementation_brief_v07_mcp.md`, and updated `.gitignore` for local scratch/config files.
- Updated `docs/mcp_smoke_test_results.md` so the setup section reflects `.mcp.json` as the active Claude Code project config.
- Added `logic_brain/execution_bus.py` with proof-carrying action envelopes, certified precondition checks, postcondition validation, action traces, rollback recommendations, and proof-bundle compatibility.
- Added the `proof_carrying_action` MCP tool in `logic_brain/mcp_tools.py` and `logic_brain/mcp_server.py`.
- Added execution-bus tests in `tests/test_execution_bus.py`, `tests/test_mcp_action_bus.py`, `tests/test_metamorphic_execution_bus.py`, and extended MCP server coverage in `tests/test_mcp_server.py`.
- Fixed CI portability issues by aligning optional MCP typing handling, adding required dev dependencies in `pyproject.toml`, and including the `examples` package in editable installs.

Recent commits:

- `9202e8a` - "Clean repo MCP artifacts and local ignores"
- `e1471b9` - "Sync handoff and completion process requirements"
- `48f45dd` - "Include examples package in editable installs"
- `d0b372c` - "Fix CI test dependencies and example package imports"
- `6b900df` - "Fix CI mypy handling for optional MCP imports"

Latest local validation seen in this session:

- `python -m pytest -q tests/test_counterfactual.py tests/test_metamorphic_counterfactual.py` -> `15 passed`
- `python -m pytest -q tests/test_integration_full_loop.py tests/test_mcp_server.py` -> `4 passed`
- `python -m pytest -q` -> `428 passed`
- `python -m ruff check logic_brain tests tools` -> clean
- `python -m mypy --strict logic_brain` -> clean
- `python -m pytest --cov=logic_brain --cov-report=term-missing --cov-fail-under=85` -> `90.29%`
- `python -m pytest -q -m metamorphic` -> `50 passed`
- GitHub Actions CI run `23356169627` on `main` -> green

## Current WIP

- Issue `#47` is in progress: first planner slice adds deterministic utility ranking, hard safety caps, and explainable decomposition directly in `CounterfactualPlanner`.
- Local uncommitted code/docs changes exist for `logic_brain/counterfactual.py`, `tests/test_counterfactual.py`, `tests/test_metamorphic_counterfactual.py`, and roadmap/handoff updates.

## Issue Queue

Open issues visible in GitHub now:

1. **#50** - Vision: v1.8 Autonomous Recovery Protocols for Failed Proof Paths
2. **#49** - Vision: v1.9 Federated Trust Domains and Cross-Agent Proof Ledger
3. **#48** - Vision: v2.0 Verified Agent Runtime (Closed-Loop Deterministic Core)
4. **#47** - Vision: v1.7 Cost-Risk-Utility Planner with Formal Tradeoff Bounds (in progress)
5. **#45** - Vision: v1.5 Adversarial Self-Play and Red-Team Reasoning Harness

Queue assessment:

- There is still no concrete next implementation issue broken out beneath the remaining vision issues.
- `#43` is closed and its core acceptance criteria are now covered by the execution-bus code, MCP integration, metamorphic tests, and green CI.
- `#47` is now underway; the current slice covers transparent branch scoring, hard safety dominance, and deterministic ranking behavior in the planner core.
- Remaining likely follow-ups for `#47` are MCP exposure and richer integration with uncertainty/contract layers if needed.

Recommended next step:

- Finish validation for the current `#47` slice, then close the issue if no further integration surface is required, or split the remaining MCP/integration work into a follow-up issue.

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
