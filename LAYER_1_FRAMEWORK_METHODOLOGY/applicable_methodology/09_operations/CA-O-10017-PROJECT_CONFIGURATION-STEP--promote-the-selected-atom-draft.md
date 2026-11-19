---
identity:
  atom_id: CA-O-10017
  ref_id: CA-O-10017
context:
  container:
    atom: CA-O-10018
  role: Operations
  form: Step
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/Step
    dependencies:
    - ANECHOIC_MODEL <+ Atom
    - ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
  tier: 3
relations:
  RUNS:
  - CA-O-10005
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10017-PROJECT_CONFIGURATION-STEP--promote-the-selected-atom-draft.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10018-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-promote-draft
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10018-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-promote-draft/CA-O-10017-PROJECT_CONFIGURATION-STEP--promote-the-selected-atom-draft.md
  source_atom_id: CA-O-10017
  source_atom_revision: 1
  source_sha256: 62ca4d74b0cf107933a50645942f1257a54f544e08ab00533b63b155d4fe126a
  original_relations_sha256: 3a56785db8f635d1e2ccfd2ed4d3cd546728d2efb59747bb89f6dc0ad8be6977
---
## Summary

Promote the selected Atom Draft

## Claim scope

One exact non-container Draft binding within [Atom Lifecycle_Promote Draft](../CA-O-10018-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-promote-draft.md).

## Claim

### Kind

Execution.

### Inputs

Selected Draft, allowed Current `targetStatus`, optional `savedArchivedAtom`, and `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Promote one Atom Draft](../CA-O-10005-PROJECT_CONFIGURATION-ACTION--promote-one-atom-draft.md).

### Outputs

The called Action's declared Outputs.
