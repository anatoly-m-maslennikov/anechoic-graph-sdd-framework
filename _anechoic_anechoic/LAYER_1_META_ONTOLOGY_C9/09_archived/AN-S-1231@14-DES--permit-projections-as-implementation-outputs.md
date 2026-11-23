---
atom_family: SPEC
atom_id: AN-S-1231
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Permit Projections as Implementation outputs

# Summary

Permit Projections as Implementation outputs

## Scope

non-authoritative view Projections delivered as Implementation outputs.

## Claim

a view Projection **may** be delivered as an Implementation output of its governing RMED **without** becoming an Atom **or** another source of truth for the facts it represents.

- its output contribution is I; its Artifact kind remains Projection **and** its content remains derived from its declared sources.
- its Standard output classification does **not** change the Content Roles, Local Tiers, identities, **or** authority of source Atoms represented inside it.

## Details

This permission concerns delivered views, not a permanent loss of actual-state authority for native Implementation. RMED → using O → I derives a realization of intent; that native I can then be source truth for what actually exists. I → using O → a dependency graph or another view produces a non-authoritative Projection.
