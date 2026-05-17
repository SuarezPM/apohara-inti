---
name: feature-documentation-update
description: Workflow command scaffold for feature-documentation-update in apohara-inti.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-documentation-update

Use this workflow when working on **feature-documentation-update** in `apohara-inti`.

## Goal

Updates documentation files (README, AUDIT) to reflect new features, behaviors, or decisions.

## Common Files

- `README.md`
- `AUDIT.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit README.md to describe new features or usage.
- Edit AUDIT.md to record audit trail or security/feature decisions.
- Document rationale, usage, and edge cases.
- Commit documentation changes.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.