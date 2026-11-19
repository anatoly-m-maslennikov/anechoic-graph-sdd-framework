---
identity:
  atom_id: CA-R-3176
  ref_id: CA-R-3176@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:36.548792+00:00'
destination:
  file:
    name: CA-R-3176@1-draft-CORE_META_MODEL-REQUIREMENT--declare-direct-component-and-atom-containment.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Declare direct Component and Atom containment

## Claim

### Prose Claim

A Component's child_of points to its direct parent Component; the parent's children is the inverse for the same direct pair. An Atom's contained_by points to its container, a Component or another Atom. An Atom's containing Component is the Component that contains it directly or through enclosing Atoms. For example, a Task may be contained_by an Epic. The child Component described by a Purpose or Manifest is distinct from the parent Component containing that Atom.

## Details

Acceptance: if B child_of A and C child_of B, A's direct children includes B, not C. If Task T is contained_by Epic E and E by Component B, T's containing Component is B. A View may show C as A's descendant.

Sources: CA-A-1462@1-draft. Task: CA-P-3080.
