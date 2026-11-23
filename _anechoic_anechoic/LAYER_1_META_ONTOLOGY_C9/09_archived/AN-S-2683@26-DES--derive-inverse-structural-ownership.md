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
  version: 26
  updated_at: 2026-10-29 07:45:27 +0400
---
## Summary

Derive inverse structural ownership

## Claim scope

the inverse `structural_children` view derived from stored `structural_parent` relations.

## Claim

ANECHOIC **must** derive the inverse `structural_children` view from stored `structural_parent` relations **and** **must not** persist that inverse separately.

## Details
