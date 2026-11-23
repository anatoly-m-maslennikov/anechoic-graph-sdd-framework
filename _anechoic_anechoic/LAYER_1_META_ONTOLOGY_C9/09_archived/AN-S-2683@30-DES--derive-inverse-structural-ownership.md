---
atom_family: SPEC
atom_id: AN-S-2683
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Derive inverse structural ownership

## Claim scope

the inverse `structural_children` view derived from stored `structural_parent` relations.

## Claim

ANECHOIC **must** derive the inverse `structural_children` view from stored `structural_parent` relations **and** **must not** persist that inverse separately.
