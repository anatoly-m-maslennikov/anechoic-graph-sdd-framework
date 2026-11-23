---
atom_family: SPEC
atom_id: AN-S-2659
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Define Subject

# Summary

Define Subject

## Scope

Subjects relating an Atom and a canonical Subject Target.

## Claim

a Subject **means** a direct Relation between an Atom **and** a canonical Subject Target, typed as GOVERNS **or** DEPENDS_ON.

## Details

- the Atom is the source; the Subject Target is the target identified by its full canonical Subject Path.
- the Subject is the Relation, **not** its target, its target's path, **or** a Term used **in** that path.
- the Relation creates no intermediate Subject object **and** no additional target identity; it does **not** make the target bearer-dependent on the source Atom.
