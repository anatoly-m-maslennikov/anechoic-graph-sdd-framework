---
atom_family: SPEC
atom_id: AN-S-1670
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 20
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Initialize Version creation timestamp

## Claim

### Prose Claim

Initialize Updated At to the actual Project-time creation instant when a new Atom Version is created. In-place edits, Status-only changes, archival, and promotion preserve the existing Version's Updated At. An ancestor-only move also preserves a descendant's Updated At. Timestamp encoding follows CA-D-270.
