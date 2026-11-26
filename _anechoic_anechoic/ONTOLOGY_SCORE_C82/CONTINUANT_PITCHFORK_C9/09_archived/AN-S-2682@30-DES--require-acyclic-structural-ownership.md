---
atom_family: SPEC
atom_id: AN-S-2682
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Require acyclic structural ownership

## Claim scope

the directed graph formed by active `structural_parent` relations.

## Claim

the directed graph formed by active `structural_parent` relations **must** be acyclic.
