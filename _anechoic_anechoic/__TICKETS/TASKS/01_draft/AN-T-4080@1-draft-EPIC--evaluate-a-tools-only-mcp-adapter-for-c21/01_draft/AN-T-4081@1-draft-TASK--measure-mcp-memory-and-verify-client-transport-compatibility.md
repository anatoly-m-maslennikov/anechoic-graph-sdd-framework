---
atom_family: TKT
atom_id: AN-T-4081
container:
  atom: AN-T-4080
priority: 2
context:
  template: task
  label: Task
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T17:14:30.747072+00:00'
---
## Summary

Measure MCP memory and verify client transport compatibility

## Acceptance

Measure idle and active RAM for C21 in the full beta runtime.
Exercise the SDK's stateless JSON mode and the existing stdio path
with supported clients, including Codex. Record session, SSE,
notification, and cancellation dependencies and the resulting
decision about the replacement.
