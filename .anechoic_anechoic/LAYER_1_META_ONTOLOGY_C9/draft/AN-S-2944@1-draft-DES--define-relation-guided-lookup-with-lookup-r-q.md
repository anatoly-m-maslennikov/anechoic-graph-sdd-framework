---
identity:
  atom_id: AN-S-2944
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 14:25:52 +0400
---
## Summary

Define Relation-guided lookup with `LOOKUP(R, q)`

## Claim

### Prose Claim

In an admitted fallback expression, `LOOKUP(R, q)` starts at the bearer of the target Property `p` and follows one existing outgoing link of declared Relation `R` at each step, in R’s declared direction. It excludes the starting bearer and returns the nearest authored value of `q` that is applicable to that bearer. Resolve `q` by full Property declaration identity and effective MODEL applicability; skip only an inapplicable Property or an absent authored occurrence. At a known end with no applicable authored value, return absence. Do not match by bare name or invent a Property slot.

A present invalid value, unresolved applicability or graph fact, multiple outgoing targets, or revisiting a bearer is an error. Follow only the Relation direction named by `R`.
