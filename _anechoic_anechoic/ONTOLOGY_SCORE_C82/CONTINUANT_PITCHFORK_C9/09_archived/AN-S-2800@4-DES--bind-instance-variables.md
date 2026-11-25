---
atom_family: SPEC
atom_id: AN-S-2800
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T23:05:46.520244+00:00"
---
## Summary

Bind instance variables

## Claim

### Prose Claim

- Validate against a fully resolved population of the declared kind and its narrower kinds. Count each logical object once, even when several Carriers refer to it.
- Apply Property occurrence bounds separately to each effective Property and bearer. Inherited Properties retain their Declaration identity. A structural Property can hold declared dependents with zero direct values.
- Bind a Python reference to the same object throughout each check. Test object identity and existing links using the supplied Project data. A scoped test applies its condition only to the matching bindings.
- Relation endpoint counts apply per endpoint. Check missing or ambiguous object and Property bindings as errors.
