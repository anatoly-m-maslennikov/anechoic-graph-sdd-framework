---
atom_family: SPEC
atom_id: AN-S-3655
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-10-19 15:53:23 +0400
---
## Summary

Restrict Direct Plan Decomposition

# Summary

Restrict Direct Plan Decomposition

## Scope

direct `DECOMPOSES_INTO` relations between Plan Atoms.

## Claim

`DECOMPOSES_INTO` **must** connect **only** distinct Plan Atoms; **any** Plan **may** decompose into other Plans regardless of their Labels, **without** requiring incoming decomposition.

## Details
