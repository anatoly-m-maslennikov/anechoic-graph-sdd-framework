---
atom_family: TKT
atom_id: AN-T-4066
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-27T12:46:01+00:00'
---

## Summary

Clear Static Python lint findings

## Acceptance

Clear the findings from the committed Ruff profile, including
F401, B006 and C901. Preserve direct test and CLI execution.
Separate mechanical fixes from changes to control flow. Verify
the changed behavior with focused tests and run locked Mypy.

## Progress

The 2026-11-27 locked Ruff run reports 23 findings, down from 239.
All 23 are in Model Generator. The fixes preserve CLI and test entry
points. Mypy and focused tests passed on the working checkout.
