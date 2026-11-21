---
atom_family: TKT
atom_id: AN-T-2919
container:
  atom: AN-T-2791
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-20T12:11:41.806187+00:00'
---
## Summary

Implement the Structure Host

## Work

Run the Structure Host as a thin, separate process. Publish a read-only snapshot API. Use one snapshot per operation, activate valid Structure changes without a restart, and retain the last valid snapshot on failure.
