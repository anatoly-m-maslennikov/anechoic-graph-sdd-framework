---
atom_family: TKT
atom_id: AN-T-3902
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T11:39:10.159425+00:00'
---
## Summary

Formalize and replay the seven-day bug fixes

## Work

Use the confirmed inventory from AN-T-3901. Independently state the intended invariant for each case from its requirements and evidence, rather than inferring correctness from the fix alone. Translate the actual historical and fixed code into Lean where supported, and document the correspondence and abstraction limits.

Reproduce each supported defect against its exact historical buggy revision, then check the fixed revision or identified worktree state. Preserve commands, revision identifiers, outcomes, and evidence. Record unsupported translations, missing revisions, and cases that cannot be reproduced.

## Acceptance

Each supported case has a stated invariant, code-linked Lean translations, a demonstrated failing replay on the exact buggy revision, and a passing check on the fixed state. Unsupported and unresolved cases are explicit and remain open.
