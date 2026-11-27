---
atom_family: TKT
atom_id: AN-T-3996
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T03:12:25.710292+00:00"
---
## Summary

Normalize Contract vocabulary and verify independent Actions

## Acceptance

Use `to` and `expect` for Solution transitions. Give the Action name,
HTTP endpoint, and route name distinct fields with the same meaning in
trace and typed HTTP. Read historical spellings at the input boundary.

Keep outcome cases explicit. Reject a cycle between required effects
before Lean generation. Use C66 to check that the language can express
reaping when a worker started and later failed, while admitting a
failure before startup.
