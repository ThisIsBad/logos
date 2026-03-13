# Development Process

This repository follows a phase-based, clean software development process.

## Core Rules

1. Work in small, reviewable units with clear scope.
2. Complete one phase before starting the next.
3. Create one commit per completed phase.
4. Run tests before every commit.
5. Keep docs and roadmap aligned with the current code state.

## Phase Workflow

For every phase or milestone:

1. Define scope and acceptance criteria.
2. Implement changes.
3. Update documentation affected by the changes.
4. Run validation (`pytest -q`, plus relevant tooling checks).
5. Commit with a message that explains intent and outcome.

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
