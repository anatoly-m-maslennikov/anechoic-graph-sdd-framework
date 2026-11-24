---
atom_family: SPEC
atom_id: AN-S-3351
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
  status: active
  version: 1
  updated_at: "2026-11-22T18:38:16.539972+00:00"
---

## Summary

Use dependency counts to review package coupling

## Claim

### Prose Claim

Count distinct resolved incoming and outgoing dependencies between in-scope
Packages. Show the contributing imports and use high counts as review
signals.
