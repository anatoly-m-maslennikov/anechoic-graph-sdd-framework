---
identity:
  atom_id: AN-S-2332
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-11-04 07:51:19 +0400
---
## Summary

Give each Projection a stable ID

## Claim

### Prose Claim


Projection identity across rebuilds.


Every Projection has one Projection ID. Its Form and Scope Unit determine its ID, and its ID determines its Form and Scope Unit. Rebuilding the same Projection retains that ID.

## Details

- A different Form or Scope Unit identifies a different Projection and requires a different ID.
- Changes to the Named Selection, its selected sources, source contents or Versions, generated content or Updated At do not change the Projection ID. Source.Named Selection describes the sources; it is not an identity component. Where Source.Atoms is recorded, each value identifies an Atom with its explicit Version.
- A change to the current Scope Unit name or Carrier path alone does not change the Projection ID.
- Projection ID identifies the derived view, not any source Atom. It does not make the Projection authoritative.
