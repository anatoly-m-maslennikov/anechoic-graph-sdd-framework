---
atom_family: TKT
atom_id: AN-T-3901
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

Inventory the seven-day functional bug fixes

## Work

Inspect tickets, Git history, and the worktree for the Operator's window 2026-11-17T15:38:02+04:00 through 2026-11-24T15:38:02+04:00. Identify confirmed functional bug fixes and distinguish candidates, non-functional changes, duplicates, and uncertain cases. Record source coverage and limits.

For each confirmed fix, record the behavior, evidence, affected paths, exact historical buggy revision, fixed revision or worktree state, and relevant regression evidence. Identify cases where an exact revision or fixed state cannot be established.

## Acceptance

The inventory accounts for the scoped sources and gives evidence and revision identifiers for each confirmed functional fix. Candidates and unsupported or uncertain cases remain explicit and available for follow-up.
