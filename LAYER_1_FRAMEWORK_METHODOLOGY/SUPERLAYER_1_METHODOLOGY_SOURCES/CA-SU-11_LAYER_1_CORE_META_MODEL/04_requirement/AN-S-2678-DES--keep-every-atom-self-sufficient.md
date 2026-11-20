---
identity:
  atom_id: AN-S-2678
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 25
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Keep every Atom self-sufficient

## Claim

### Prose Claim


Atom Revisions and their applicable Properties.


**every** Atom Revision **must** carry its applicable Properties within its own Markdown Carrier so that its own declared content can be read **without** reconstructing it from a filename **or** directory placement.

- the applicable model determines which Properties are required, optional, **or** inapplicable; self-sufficiency does **not** invent missing Properties **or** permit an invalid value.
- a Relation **to** another Atom remains declared **only** on its registered owning endpoint; the other endpoint **and** inverse views are resolved from that declaration, **not** independently copied.
- self-sufficiency does **not** require copying the referenced Atom, governing model, **or** inherited Settings authority into this Atom.
