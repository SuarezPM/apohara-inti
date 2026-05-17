---
name: feature-implementation-with-tests
description: Workflow command scaffold for feature-implementation-with-tests in apohara-inti.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-implementation-with-tests

Use this workflow when working on **feature-implementation-with-tests** in `apohara-inti`.

## Goal

Implements a new backend or frontend feature together with corresponding unit/integration tests.

## Common Files

- `packages/backend/*.py`
- `packages/backend/tests/test_*.py`
- `packages/frontend/src/*.tsx`
- `packages/frontend/src/lib/*.ts`
- `packages/frontend/src/lib/*.test.ts`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Implement feature logic in backend or frontend source files.
- Add or update corresponding test files to cover the new logic.
- Update related files (e.g., API routes, helpers, or UI components) as needed.
- Run tests to verify correctness.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.