---
atom_family: SPEC
atom_id: AN-S-77
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Commit each folder lifecycle action

# Commit each folder lifecycle action

## Test case

Given a non-empty Git-trackable folder, **when** it is added, structurally moved, updated across multiple contained files, **and** removed **in** successive operations, **then** **every** operation produces exactly one folder-subject commit **and** one completed Journal event, uses `ADD`, `MOVE`, `UPDATE`, **and** `REMOVE` respectively, **and** advances the logger-owned folder revision **only** while a present result exists.

## Sources

- [CA-R-805 — Serialize repository Git mutations through one logical gate](../04_requirement/CA-R-805-COMMIT_CHANGE_SET-RULE--serialize-admitted-local-commits-through-one-logical-gate.md)
- [CA-M-087 — Process one project-path action](../../05_method/CA-M-087-TOOLS-ENG_DECISION--process-one-project-path-action.md)
