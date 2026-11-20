---
identity:
  atom_id: AN-S-3023
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:39.127648+00:00'
---
## Summary

Preserve identity and version for status transitions

## Claim

### Prose Claim

A status-only transition of an Atom must preserve its Atom ID and Version.

## Details

Acceptance: Changing a Task from Backlog to Active leaves its Atom ID and Version unchanged.

Sources: CA-A-1464@1-draft. Task: CA-P-3086.
