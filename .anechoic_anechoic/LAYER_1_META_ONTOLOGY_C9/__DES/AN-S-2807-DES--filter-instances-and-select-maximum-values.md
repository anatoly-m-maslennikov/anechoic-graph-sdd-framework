---
atom_family: SPEC
atom_id: AN-S-2807
structure:
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

Filter instances and select maximum values

## Claim

### Prose Claim


- Select matching instances of the declared kind and its narrower kinds from an explicit Project snapshot.
- Evaluate predicates on each candidate, with Python's short-circuit rules. Resolve references to their target identity. An evaluated predicate with a missing, invalid or unresolved value raises an error.
- Each matching instance contributes one valid scalar. Return the greatest scalar under the applicable Format. Compare datetimes by instant.
- Reject empty, incomplete or incompatible input. Selection and comparison are read-only.
