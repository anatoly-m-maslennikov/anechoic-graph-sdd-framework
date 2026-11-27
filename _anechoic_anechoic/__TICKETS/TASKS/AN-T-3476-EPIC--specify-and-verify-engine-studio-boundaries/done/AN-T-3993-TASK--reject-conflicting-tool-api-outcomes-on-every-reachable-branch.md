---
atom_family: TKT
atom_id: AN-T-3993
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:33:22.091895+00:00"
---
## Summary

Reject conflicting Tool API outcomes on every reachable branch

## Acceptance

Check each reachable terminal and response field. Reproduce the false pass where a 200 success hides a 503 success with no envelope. Keep a known status conflict even when another field is missing. Verify the corrected 200 case and include the malformed branch as a regression.
