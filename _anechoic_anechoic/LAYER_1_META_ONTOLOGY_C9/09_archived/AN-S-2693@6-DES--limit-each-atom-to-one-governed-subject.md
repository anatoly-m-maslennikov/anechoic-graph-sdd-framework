---
atom_family: SPEC
atom_id: AN-S-2693
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-29 07:17:20 +0400
---
## Summary

Limit each Atom to one governed Subject

# Summary

Limit each Atom to one governed Subject

## Scope

The direct GOVERNS Subject Relations recorded in an Atom's Subjects.

## Claim

An Atom **may** have zero or one direct GOVERNS Subject Relation. No Atom's Subjects **may** contain more than one direct GOVERNS Subject Relation.

## Details

This Rule limits cardinality only. It does not require an Atom to have a GOVERNS Subject. The Subjects collection is optional, and DEPENDS_ON relations are not limited by this Rule.
