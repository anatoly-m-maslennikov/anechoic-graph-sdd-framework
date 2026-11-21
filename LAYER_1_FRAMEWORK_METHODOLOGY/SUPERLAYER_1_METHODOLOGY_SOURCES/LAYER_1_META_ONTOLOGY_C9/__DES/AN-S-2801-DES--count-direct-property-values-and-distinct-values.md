---
atom_family: SPEC
atom_id: AN-S-2801
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Count direct Property values and distinct values

## Claim

### Prose Claim

- A direct-value count measures the actual values of one Property on one bearer. Equal values contribute separate occurrences. An absent optional Property contributes zero.
- A distinct-value count compares values using their declared Format. Compare references by resolved identity. Count dependent Property names separately.
- Report an error when the bearer, Property or value cannot be resolved.
