---
identity:
  atom_id: AN-S-2769
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: draft
  version: 31
  updated_at: 2026-11-05 06:15:15 +0400
---
## Summary

Serialize Authored Direct Relations on Their Owning Atoms

## Claim

### Prose Claim


Authored direct semantic relations.


An Atom **must** record its immediate Container once in `Header.Container` as a mapping with exactly one of `scope_unit` or `atom`. The `scope_unit` reference uses the Scope Unit’s stable ID. Its declared Container represents the `IS_CONTAINED_BY` fact; do not add a second `relations.IS_CONTAINED_BY` entry. Other authored direct semantic Relations **must** be serialized once under `relations.<RELATION_KIND>` on the Atom that owns their declared direction as nonempty unordered collections of unique canonical target references. `Header.Relations` is optional when no such Relations are present. Target position and source-file order are nonsemantic; validation **must not** require sorting or order normalization. Each Relation's declared direction, endpoint validity, and other semantics remain applicable.

## Details

Serialize only the declared direct direction, never a second declaration for its derived inverse. `CONTAINS` remains a derived parent view and is not serialized on the parent. An Atom child stores its parent reference in `Header.Container`; a child-only change does not write the parent Carrier or create a parent Version. The Relation's spelling does not determine its direct direction.

CA-D-264 and CA-D-266 govern agreement between declared Container, Carrier placement and readback of the same containment fact. This Decision does not introduce another stored containment fact or a runtime relation key.
