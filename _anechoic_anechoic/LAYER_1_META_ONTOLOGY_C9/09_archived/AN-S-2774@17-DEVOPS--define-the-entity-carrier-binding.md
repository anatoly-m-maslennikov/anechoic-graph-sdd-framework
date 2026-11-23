---
atom_family: SPEC
atom_id: AN-S-2774
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 17
  updated_at: 2026-10-30 14:42:22 +0400
---
## Summary

Define the Entity Carrier binding

## Claim scope

Carrier bindings of Entities.

## Claim

the Carrier Property of an Entity **means** its binding **to** the Carrier that stores **or** represents it.

## Details

- write this Property as `(Entity).Carrier`, using the actual Entity path, such as `Atom.Carrier` **or** `Scope Unit.Carrier`.
- the binding follows IS_CARRIED_BY.
- the Property refers **to** a Carrier; the referenced Carrier remains a Primary Entity.
