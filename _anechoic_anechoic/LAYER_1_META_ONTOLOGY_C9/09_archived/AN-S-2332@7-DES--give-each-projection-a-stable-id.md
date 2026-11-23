---
atom_family: SPEC
atom_id: AN-S-2332
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Give each Projection a stable ID

# Summary

Give each Projection a stable ID

## Scope

Projection identity across rebuilds.

## Claim

Every Projection has one Projection ID. The same Projection Type, named source selection and source of truth identify the same Projection and keep the same ID across rebuilds.

## Details

- A different Type, named source selection or source of truth identifies a different Projection and requires a different ID.
- Changes to source contents, source Versions, the artifacts selected by the same selection, generated content or Updated At do not change the Projection ID.
- A change to the current Scope Unit name or Carrier path alone does not change the Projection ID.
- Projection ID identifies the derived view, not any source Atom. It does not make the Projection authoritative.
