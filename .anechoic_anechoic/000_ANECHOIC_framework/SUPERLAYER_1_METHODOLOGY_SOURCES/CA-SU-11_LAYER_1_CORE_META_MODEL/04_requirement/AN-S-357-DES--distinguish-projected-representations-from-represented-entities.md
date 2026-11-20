---
atom_family: SPEC
atom_id: AN-S-357
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Distinguish projected representations from represented Entities

## Claim

### Prose Claim


Representations inside a Projection and the Entities they represent.


a representation inside a Projection **must** remain distinct from the Entity it represents.

- depicting an existing Artifact **or** Scope Unit does **not** create another authoritative Artifact **or** Scope Unit.
- a representation **may** identify a source Entity **or** a derived element admitted by the Projection specification; source identities **and** traceability remain governed by CA-R-2535.
- this boundary introduces no separate Projection Element Term, lifecycle, **or** independently maintained authority.
