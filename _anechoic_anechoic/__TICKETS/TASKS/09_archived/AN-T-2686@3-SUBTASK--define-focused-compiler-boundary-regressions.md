---
atom_family: TKT
atom_id: AN-T-2686
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 10:35:14 +0400
---
## Summary

Define focused compiler boundary regressions

# Summary

Define focused compiler boundary regressions

## Objective

Define the separate focused regression Task for the compiler and Journal-boundary repair after CA-P-2623 identifies the smallest safe implementation surface. Keep test design separate from compiler refactoring because the combined work may exceed one 15-minute Task.

## Details

This is a bounded follow-up Task, currently Backlog. Use frozen or explicitly admitted fixtures only; cover approval construction, failed-publication recovery, independent recording_error handling, partial results and the no-universal-Journal-gate behavior described by CA-C-583. Do not edit source or tests while this planning record is Backlog. No live MCP, release, deployment, replay or full-suite run.

## Definition of Done

Produce a short table-driven focused test plan with exact fixture inputs, expected business Journal records, technical diagnostics and caller-visible outcomes. Activate only after CA-P-2623 is reviewed; passing tests alone does not resolve the source-level Problem or admit a runtime binding.
