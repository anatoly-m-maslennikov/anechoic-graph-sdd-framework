---
atom_family: SPEC
atom_id: AN-S-1397
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Remove one disabled Tool projection

## Claim

### Prose Claim

Verify that rebuilding the registration asset after a configured provider or route is disabled removes that callable identity while retaining every other eligible configured entry.

## Details

Disable a previously exposed configured entry and rebuild the asset. The registry excludes it and retains all other eligible configured entries; no stale exposure remains.
