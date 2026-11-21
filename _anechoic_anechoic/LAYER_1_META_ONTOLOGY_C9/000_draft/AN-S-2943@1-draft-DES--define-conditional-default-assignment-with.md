---
atom_family: SPEC
atom_id: AN-S-2943
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 14:25:52 +0400
---
## Summary

Define conditional default assignment with `?==`

## Claim

### Prose Claim

Write conditional default assignment as `p ?== e`. It keeps an authored value of `p`; when `p` is absent, it sets the first available valid value in the Model under the ordered fallback rule. A present invalid value is not absence. This syntax does not itself write a Carrier; persistence belongs to an adapter or Delivery rule.
