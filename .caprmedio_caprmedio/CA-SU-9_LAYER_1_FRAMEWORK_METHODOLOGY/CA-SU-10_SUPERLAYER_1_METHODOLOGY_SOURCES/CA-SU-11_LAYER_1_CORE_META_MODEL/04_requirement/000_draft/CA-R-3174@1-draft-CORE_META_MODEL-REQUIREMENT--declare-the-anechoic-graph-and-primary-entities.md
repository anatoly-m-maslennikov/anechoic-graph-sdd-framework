---
identity:
  atom_id: CA-R-3174
  ref_id: CA-R-3174@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:29.828572+00:00'
destination:
  file:
    name: CA-R-3174@1-draft-CORE_META_MODEL-REQUIREMENT--declare-the-anechoic-graph-and-primary-entities.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Declare the Anechoic graph and primary entities

## Claim

### Prose Claim

A Model has a Graph, an eDSL, and Carriers. A Graph consists of Nodes and Relations. Artifact and Ephemeral narrow Node. Atom, Event Record, Component, and Package narrow Artifact. Spec Atom, Ticket Atom, and PMETA Atom narrow Atom. Project narrows Component; Component Package narrows Package. A Component has a Component Spec Section and a Component Package. A Package may contain Packages and Modules; a Module may contain Units. The eDSL is Python for writing Manifests; Format and Cardinality belong to the eDSL.

A View presents information derived from source Atoms and Relations. A View is the new name for the Current Projection; Workspace and its editable SQL View belong to the Workbench model.

## Details

Acceptance: a Project is a Component and an Artifact; a Component Package is a Package; an Ephemeral Node is not thereby an Artifact. A derived View does not become the authored source of its facts.

Sources: CA-A-1462@1-draft. Task: CA-P-3080.
