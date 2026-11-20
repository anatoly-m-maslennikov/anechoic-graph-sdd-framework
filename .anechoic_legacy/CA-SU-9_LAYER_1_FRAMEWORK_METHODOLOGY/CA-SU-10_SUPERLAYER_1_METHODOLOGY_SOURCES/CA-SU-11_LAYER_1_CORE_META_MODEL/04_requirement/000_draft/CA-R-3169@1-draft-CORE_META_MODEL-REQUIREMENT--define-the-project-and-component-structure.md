---
identity:
  atom_id: CA-R-3169
  ref_id: CA-R-3169@1-draft
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
  updated_at: '2026-11-18T22:02:54.132508+00:00'
destination:
  file:
    name: CA-R-3169@1-draft-CORE_META_MODEL-REQUIREMENT--define-the-project-and-component-structure.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define the Project and Component structure

## Claim

### Prose Claim

A Project has a root Project Component. A Component has a Component Spec Section and a Component Package in REAL and may contain child Components. Component code may contain ordinary Packages. A Module is one source file; a Unit is a function, class, or method. `child_of` points to the parent Component and its inverse supplies children. Layers order siblings where needed. Within an ordered sibling group, imports may target only upstream siblings with lower layer numbers. Downstream imports are forbidden. Unordered siblings have no layer restriction. Each Atom tier is local to its containing Component.

## Details

Acceptance: Anechoic has exactly three direct children: Meta-ontology, Meta-methodology, and Engine Studio. Kernel Mixer, Backend Deck, IWE Console, and MCP Patchbay are children of Engine Studio, not direct children of Anechoic.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
