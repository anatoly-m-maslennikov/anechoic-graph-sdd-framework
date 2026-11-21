---
atom_family: SPEC
atom_id: AN-S-1602
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: active
  version: 32
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Permit confidence-threshold defaults and overrides

## Claim

### Prose Claim


the source of a Confidence Threshold value.


a Confidence Threshold **must** take its value from applicable direct Operator input, an explicit Property on the current Plan, the nearest enclosing Hub Plan with an explicit Property, **or** the Framework Instance Settings default; the Plan-containment chain follows `IS_CONTAINED_BY` toward the nearest enclosing Plan, **not** Label spelling.
