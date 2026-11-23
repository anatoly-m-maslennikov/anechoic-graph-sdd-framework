---
atom_family: TKT
atom_id: AN-T-1998
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-10-05 01:20:00 +0400
---
## Summary

Reject raw duplicate keys and frontier identity collisions

# Summary

Reject raw duplicate keys and frontier identity collisions

## Disposition

Resolved in the Journal source contract: raw JSON duplicate object keys are
rejected before parse, and Event IDs must be unique across the captured frontier.
CA-E-577 preserves expected-failure evidence; no implementation claim is made.
