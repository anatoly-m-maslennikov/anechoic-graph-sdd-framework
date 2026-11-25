---
atom_family: SPEC
atom_id: AN-S-2683
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 31
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Derive inverse structural ownership

## Claim

### Prose Claim


the inverse `structural_children` view derived from stored `structural_parent` relations.


ANECHOIC **must** derive the inverse `structural_children` view from stored `structural_parent` relations **and** **must not** persist that inverse separately.
