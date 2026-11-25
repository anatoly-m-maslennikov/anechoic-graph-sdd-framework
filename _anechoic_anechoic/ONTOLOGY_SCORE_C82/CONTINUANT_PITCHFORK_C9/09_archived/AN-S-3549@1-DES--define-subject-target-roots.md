---
atom_family: SPEC
atom_id: AN-S-3549
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-21 01:47:52 +0400
---
## Summary

Define Subject Target Roots

# Summary

Define Subject Target Roots

## Scope

the first named component of a canonical Subject Target path.

## Claim

a canonical Subject Target path **must** begin with exactly one registered root:
`Entity` for what a Claim governs or `Method` for how a Method Claim guides work.

## Details

the roots are namespaces, not a hierarchy between Entity and Method. a Scope
Unit path, carrier path, owner path, or implementation-language folder does not
qualify a Subject Target unless it is explicitly part of the canonical target.
