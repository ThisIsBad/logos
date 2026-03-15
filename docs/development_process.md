# Development Process

This repository follows a phase-based, clean software development process.

## Core Rules

1. Work in small, reviewable units with clear scope.
2. Complete one phase before starting the next.
3. Create one commit per completed phase.
4. Run tests before every commit.
5. Keep docs and roadmap aligned with the current code state.
6. Plan implementation work as GitHub Issues.
7. Work issues in priority order (one issue in progress at a time).
8. Keep traceability strict: one primary issue per implementation commit/PR.
9. Apply this process to this repository itself (dogfooding is mandatory).

## Phase Workflow

For every phase or milestone:

1. Define scope and acceptance criteria.
2. Create or update GitHub Issues for each scoped unit.
3. Select the next issue by priority and implement it end-to-end.
4. Update documentation affected by the changes.
5. Run validation (`pytest -q`, plus relevant tooling checks).
6. Commit with a message that explains intent and outcome.
7. Push to GitHub (`git push`).

## GitHub Issue Workflow

- Track all non-trivial work in GitHub Issues.
- Keep issue titles action-oriented and acceptance criteria explicit.
- Link commits and pull requests back to the corresponding issue.
- Close issues only after validation is green.
- Follow strict ordering: do not start the next issue before finishing the current one.

### Auto-Issue Continuation (Backlog Refill)

To keep delivery continuous, backlog refill is event-driven (not periodic by count):

1. If `open issues < 2` and no issue is currently in progress, run the autopilot.
2. Refill up to target (`open issues ~= 5`), max 5 new issues per run.
3. New issues must follow the required issue template in this document.
4. Avoid duplicates against existing open/closed titles.
5. Resume strict `WIP=1` execution immediately after refill.

Tooling command:

```bash
python tools/issue_autopilot.py --min-open 2 --target-open 5 --max-create 5
```

This command is dry-run by default. To create issues:

```bash
python tools/issue_autopilot.py --min-open 2 --target-open 5 --max-create 5 --execute
```

### Required Issue Template

Each issue must include:

- Goal
- Scope
- Non-scope
- Acceptance Criteria (testable)
- Test Plan (local + CI checks)
- Risk Notes

Use this skeleton when creating new issues:

```md
## Goal
<What outcome should be achieved?>

## Scope
- <in-scope item>

## Non-scope
- <explicitly out of scope>

## Acceptance Criteria
- [ ] <testable criterion>

## Test Plan
- Local: <commands>
- CI: <expected jobs>

## Risk Notes
- <known risk and mitigation>
```

## Branch and Commit Hygiene

- Do not mix unrelated work in one commit.
- Prefer additive, reversible changes.
- Avoid forceful or destructive git operations.
- Keep commit history readable and milestone-oriented.

## Quality Gates

Before moving to the next phase:

- Tests pass.
- Public API impact is documented.
- Roadmap/progress docs are updated.
- Open technical risks are captured.

### Developer Preflight (required before every implementation commit)

Run these commands locally:

```bash
python -m pytest -q
python -m ruff check logic_brain/ tests/ tools/
python -m mypy --strict logic_brain
python -m pytest --cov=logic_brain --cov-report=term-missing --cov-fail-under=85
python -m pytest -q -m metamorphic
```

If one gate fails, do not commit. Fix first.

## Definition of Done (Issue Closure)

An issue may be closed only when all items are true:

- Acceptance criteria are fully met.
- Local preflight is green.
- CI is green for the related commit/PR.
- Documentation is updated where behavior/process changed.
- Commit/PR reference is linked in the issue.

## Autonomous Execution Mode (Silent Autopilot)

When the user is away or explicitly enables autonomous work, the agent operates
in **Silent Autonomy Mode**. This section is the canonical reference so that any
session — even without prior context — knows the rules.

### Default behaviour

- **No chat output.** The agent works silently: issue-first, WIP=1, full
  preflight gates, commit, push, next issue.
- Progress is visible **only through GitHub** (commits, closed issues).
- The agent does **not** produce status updates, summaries, or progress
  reports in the chat unless explicitly requested.

### When to break silence

The agent sends a chat message **only** when one of these conditions is met:

1. **Hard blocker** — a problem that cannot be resolved autonomously:
   - Missing credentials, permissions, or repository access errors.
   - A preflight gate that fails repeatedly after two self-repair attempts.
   - An irreversible decision that requires explicit user approval
     (e.g., force-push, breaking API change outside the roadmap).
2. **Empty queue + autopilot exhausted** — all open issues are closed *and*
   `tools/issue_autopilot.py --execute` has no remaining catalog entries to
   create.
3. **Explicit user request** — the user writes `status`, `report`, or any
   direct question.

Everything else (successful commits, issue closures, gate results) stays
silent and is traceable via `git log` / GitHub.

### Session handoff

When a session ends (token limit, timeout, or user-initiated stop):

1. Write `docs/new_session_handoff.md` with:
   - Last completed issue (number + commit SHA).
   - Current WIP issue (if any).
   - Open issue queue snapshot.
   - Any known blockers or decisions pending.
2. Do **not** commit this file (it is `.gitignore`-style transient).

A new session can read this file to resume without user re-explanation.

## Dogfooding Rule

- Process changes in this document must be applied immediately to the next issue.
- If practice diverges from this process, update this document first, then continue.

## References

- API contract: `STABILITY.md`
- Roadmap: `docs/roadmap_v013_v020.md`
- Release process: `docs/release_playbook.md`
