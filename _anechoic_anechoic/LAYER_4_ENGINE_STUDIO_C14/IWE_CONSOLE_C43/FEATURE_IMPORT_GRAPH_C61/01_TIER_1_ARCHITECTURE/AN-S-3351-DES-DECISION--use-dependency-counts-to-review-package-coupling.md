---
atom_family: SPEC
atom_id: AN-S-3351
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-26T16:38:46.240829+00:00'
---

## Summary

Use dependency counts to review package coupling

## Claim

### Prose Claim

Count distinct resolved incoming and outgoing dependencies between in-scope
Packages. Show the contributing imports and use high counts as review
signals.
