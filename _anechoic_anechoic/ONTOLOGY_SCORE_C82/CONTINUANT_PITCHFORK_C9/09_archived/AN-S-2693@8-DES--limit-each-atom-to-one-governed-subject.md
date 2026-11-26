---
atom_family: SPEC
atom_id: AN-S-2693
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-25T22:11:27.233535+00:00"
---
## Summary

Limit each Atom to one governed Subject

## Claim

### Prose Claim


The direct GOVERNS Subject Relations recorded in an Atom's Subjects.


An Atom **may** have zero or one direct GOVERNS Subject Relation. No Atom's Subjects **may** contain more than one direct GOVERNS Subject Relation.

## Details

This Rule limits cardinality only. It does not require an Atom to have a GOVERNS Subject. The Subjects collection is optional, and DEPENDS_ON relations are not limited by this Rule.
