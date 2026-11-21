---
atom_family: SPEC
atom_id: AN-S-3006
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:36.548792+00:00'
---
## Summary

Declare direct Component and Atom containment

## Claim

### Prose Claim

A Component's child_of points to its direct parent Component; the parent's children is the inverse for the same direct pair. An Atom's contained_by points to its container, a Component or another Atom. An Atom's containing Component is the Component that contains it directly or through enclosing Atoms. For example, a Task may be contained_by an Epic. The child Component described by a Purpose or Manifest is distinct from the parent Component containing that Atom.

## Details

Acceptance: if B child_of A and C child_of B, A's direct children includes B, not C. If Task T is contained_by Epic E and E by Component B, T's containing Component is B. A View may show C as A's descendant.

Sources: CA-A-1462@1-draft. Task: CA-P-3080.
