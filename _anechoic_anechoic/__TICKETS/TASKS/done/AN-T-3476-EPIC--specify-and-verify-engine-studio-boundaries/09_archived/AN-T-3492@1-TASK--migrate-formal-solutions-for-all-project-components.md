---
atom_family: TKT
atom_id: AN-T-3492
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T23:42:16.000000+00:00'
---
## Summary

Migrate or add primary formal Solutions for all Project Components

## Work

For every Project Component in the live declared inventory at execution
time, migrate existing primary Solution claims into the formal eDSL or
add a primary formal Solution. Reuse valid formal Solutions. Treat
Component Seeds as a separate entity.

Include Engine Studio (C14), Release (C27), User Setup (C65), and all
their declared descendants. Preserve each Solution's white-box role,
pin it to the exact Contract revision, and run the top-down checks
before AN-T-3485.

## Acceptance

Each Project Component has one primary formal Solution pinned to its current Contract, or has a specific evidence-backed unresolved gap left open. Report the live inventory coverage and top-down check results; keep unresolved checks open and complete the checks before AN-T-3485 begins. Do not rely on a fixed prior count.

## Open decisions

C67's Active Contract and Decision serve accepted Structure bytes.
The Draft path reconstructs canonical JSON from admitted rows. Define the
agreed representation and generation identity before activating that pair.
