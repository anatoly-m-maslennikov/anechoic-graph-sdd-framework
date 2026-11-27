---
atom_family: TKT
atom_id: AN-T-3986
container:
  component: C50
priority: 2
context:
  template: task
  label: Task
state:
  status: "in_queue"
  version: 1
  updated_at: "2026-11-26T12:04:07.755101+00:00"
---
## Summary

Run the Lean check in the Model update flow

## Work

Use the existing Model update flow to check changed Model candidates with Lean before admission. Include changes to Project Config that affect the Model.

## Acceptance

- Studio startup remains Lean-free.
- A failed Lean check reports the error and keeps the last admitted Model serving.
- Functional tests exercise the check through the Model update flow.
