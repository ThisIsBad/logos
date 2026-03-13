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

## References

- API contract: `STABILITY.md`
- Roadmap: `docs/roadmap_v013_v020.md`
- Release process: `docs/release_playbook.md`
