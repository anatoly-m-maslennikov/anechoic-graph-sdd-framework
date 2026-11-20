---
identity:
  atom_id: AN-S-2995
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: draft
  version: 15
  updated_at: '2026-11-12T18:31:37.011484+00:00'
---

## Summary

Define Cardinality Notation

## Claim

### Prose Claim

- Allowed bounds use non-negative integers. Both ends of a range are inclusive.
- Each declared named Property occurs at most once per bearer. An explicit occurrence bound governs presence. Without it, a positive direct-value minimum requires a leaf Property. A zero minimum leaves presence optional.
- Direct-value counts measure values on one occurrence. A structural Property can have dependents and zero direct values.
- A dependent Property count measures distinct selected names on the bearer. An immediate count includes one level. A recursive count includes all selected descendants.
- Each Relation endpoint has an independent count of matching links per selected endpoint. The inverse swaps the two counts.
- An omitted count is unspecified. A comparison tests the actual count separately from the allowed bound.
