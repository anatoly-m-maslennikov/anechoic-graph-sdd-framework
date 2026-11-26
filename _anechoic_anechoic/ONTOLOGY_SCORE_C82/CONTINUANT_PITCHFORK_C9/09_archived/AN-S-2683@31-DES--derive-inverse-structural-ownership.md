---
atom_family: SPEC
atom_id: AN-S-2683
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 31
  updated_at: "2026-11-25T20:23:22.121912+00:00"
---
## Summary

Derive inverse structural ownership

## Claim

### Prose Claim


the inverse `structural_children` view derived from stored `HAS_STRUCTURAL_PARENT` relations.


ANECHOIC **must** derive the inverse `structural_children` view from stored `HAS_STRUCTURAL_PARENT` relations **and** **must not** persist that inverse separately.
