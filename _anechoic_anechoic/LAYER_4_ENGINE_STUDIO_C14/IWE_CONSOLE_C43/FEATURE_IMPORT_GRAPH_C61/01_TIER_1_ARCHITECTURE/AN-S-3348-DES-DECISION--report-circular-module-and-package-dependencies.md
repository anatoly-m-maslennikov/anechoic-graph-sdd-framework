---
atom_family: SPEC
atom_id: AN-S-3348
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
  updated_at: "2026-11-22T18:38:16.527994+00:00"
---

## Summary

Report circular module and package dependencies

## Claim

### Prose Claim

Group resolved internal dependencies into cycles at Module and Package level.
Show the import sites that form a cycle and use the result for review.
