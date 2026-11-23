---
atom_family: SPEC
atom_id: AN-S-3353
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3083@6
state:
  status: "active"
  version: 1
  updated_at: "2026-11-22T18:38:16.546092+00:00"
---

## Summary

Detect Python import order failures

## Claim

### Prose Claim

Separate imports evaluated during Module initialization from deferred
imports. Confirm an import-order failure with a reached read of a partially
initialized name.
