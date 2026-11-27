---
atom_family: SPEC
atom_id: AN-S-3353
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-26T16:38:46.236453+00:00'
---

## Summary

Detect Python import order failures

## Claim

### Prose Claim

Separate imports evaluated during Module initialization from deferred
imports. Confirm an import-order failure with a reached read of a partially
initialized name.
