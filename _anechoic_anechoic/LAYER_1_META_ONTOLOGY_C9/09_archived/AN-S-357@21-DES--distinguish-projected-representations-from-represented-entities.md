---
atom_family: SPEC
atom_id: AN-S-357
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-30 16:12:37 +0400
---
## Summary

Distinguish projected representations from represented Entities

## Claim scope

Representations inside a Projection and the Entities they represent.

## Claim

a representation inside a Projection **must** remain distinct from the Entity it represents.

- depicting an existing Artifact **or** Scope Unit does **not** create another authoritative Artifact **or** Scope Unit.
- a representation **may** identify a source Entity **or** a derived element admitted by the Projection specification; source identities **and** traceability remain governed by CA-R-1746.
- this boundary introduces no separate Projection Element Term, lifecycle, **or** independently maintained authority.
