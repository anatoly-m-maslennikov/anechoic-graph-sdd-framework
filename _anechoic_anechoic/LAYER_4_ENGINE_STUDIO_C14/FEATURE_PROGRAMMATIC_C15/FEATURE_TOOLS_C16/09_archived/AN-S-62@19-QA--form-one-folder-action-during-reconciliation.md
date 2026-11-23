---
atom_family: SPEC
atom_id: AN-S-62
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Form one folder action during reconciliation

# Form one folder action during reconciliation

## Test case

Given multiple Git-admitted changes below one non-root folder **and** an explicitly declared grouping policy, **when** COMMIT_AUTOMATION reconciles the current repository frontier, **then** its pure manager forms one folder-subject action with one frozen ordered entry set **and** preserves **every** contributing event identity. COMMIT_TRIGGER does **not** scan **or** group the repository.

## Sources

- [CA-M-087 — Process one project-path action](../../05_method/CA-M-087-TOOLS-IMPL_METHOD--process-one-project-path-action.md)
