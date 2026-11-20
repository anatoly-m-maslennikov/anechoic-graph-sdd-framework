---
identity:
  atom_id: AN-S-2951
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-06 19:33:59 +0400
---

## Summary

Declare Property calculation specialization

## Claim

### Prose Claim

A Declaration supplies a Property calculation as `p == expression` for its selected kind.

- The calculation from the most specific applicable Declaration replaces an inherited calculation for the same Property.
- A missing local calculation leaves the inherited calculation applicable.
- An ambiguous most-specific calculation is a conflict.
- Inherited formats, cardinalities, allowed-value rules and Relation constraints remain applicable.
- Separate applicable Rule Claims still constrain the result.

Replacement selects the calculation. It does not change the receiver's identity or store a value.
