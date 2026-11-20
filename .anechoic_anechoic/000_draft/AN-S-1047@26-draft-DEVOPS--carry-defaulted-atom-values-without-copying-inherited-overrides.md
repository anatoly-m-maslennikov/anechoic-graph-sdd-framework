---
identity:
  atom_id: AN-S-1047
context:
  container:
    component: C00
  tier: 3
  lens: DevOps
state:
  status: draft
  version: 26
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Carry defaulted Atom values without copying inherited overrides

## Claim scope

defaulted Atom values and inherited external settings.

## Claim

a writer **must** preserve the distinction between a defaulted Atom Property **and** an inherited external setting:

- a required Atom value selected by applying a default is still carried at its canonical internal location; equality **to** that default does **not** permit omitting the value.
- an unselected optional override remains absent; do **not** copy an inherited effective setting into a locally selected override.
- retain an explicit override even **when** it currently equals the inherited value, because later upstream changes **must not** change that selection.
