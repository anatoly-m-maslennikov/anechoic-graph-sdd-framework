---
atom_family: TKT
atom_id: AN-T-4001
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:38:32.420072+00:00"
---
## Summary

Generate provider tests from the pinned HTTP Contract

## Acceptance

Use Schemathesis in a test-only environment for the selected HTTP Action. Run generated valid and invalid requests against the isolated real provider. Assert the exact 200, 400 and controlled 500 outcomes and schemas in deterministic tests. Verify one deliberately bad response fails. Retain source and candidate evidence.
