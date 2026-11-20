---
identity:
  atom_id: AN-S-2947
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 17:25:05 +0400
---

## Summary

Select direct Property values with VALUES

## Claim

### Prose Claim

`VALUES(p)` selects the actual direct value occurrences of the selected Property expression `p`. Equal values remain distinct occurrences. It does not recursively walk dependent Properties or read value constraints as actual values. A known absent optional Property contributes an empty selection; unresolved or malformed bearer, Property population or value is an error, not an empty selection. Existing applicable cardinality and Format rules continue to apply.
