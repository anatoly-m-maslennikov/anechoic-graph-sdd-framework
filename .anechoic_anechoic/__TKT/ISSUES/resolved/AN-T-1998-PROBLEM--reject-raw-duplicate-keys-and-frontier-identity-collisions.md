---
identity:
  atom_id: AN-T-1998
context:
  container:
    component: C16
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Reject raw duplicate keys and frontier identity collisions

## Disposition

Resolved in the Journal source contract: raw JSON duplicate object keys are
rejected before parse, and Event IDs must be unique across the captured frontier.
CA-E-577 preserves expected-failure evidence; no implementation claim is made.
