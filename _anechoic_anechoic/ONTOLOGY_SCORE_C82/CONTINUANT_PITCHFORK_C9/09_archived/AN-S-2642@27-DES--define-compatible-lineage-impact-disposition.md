---
atom_family: SPEC
atom_id: AN-S-2642
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 27
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define compatible Lineage Impact disposition

## Claim scope

`compatible` Lineage Impact dispositions.

## Claim


When a Lineage Impact analysis addresses an Atom, `compatible` must mean the child remains valid against the parent Revision required by the gate and traversal stops without a child update; a pinned earlier Revision does not establish compatibility where the new Revision is required.

