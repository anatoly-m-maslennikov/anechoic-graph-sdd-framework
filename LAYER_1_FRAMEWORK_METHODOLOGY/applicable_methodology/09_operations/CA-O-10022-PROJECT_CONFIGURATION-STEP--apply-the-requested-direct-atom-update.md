---
identity:
  atom_id: CA-O-10022
  ref_id: CA-O-10022
context:
  container:
    atom: CA-O-10023
  role: Operations
  form: Step
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/Step
    dependencies:
    - CAPRMEDIO_MODEL <+ Atom
    - CAPRMEDIO_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
  tier: 3
relations:
  RUNS:
  - CA-O-10000
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10022-PROJECT_CONFIGURATION-STEP--apply-the-requested-direct-atom-update.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10023-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom-directly
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10023-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom-directly/CA-O-10022-PROJECT_CONFIGURATION-STEP--apply-the-requested-direct-atom-update.md
  source_atom_id: CA-O-10022
  source_atom_revision: 1
  source_sha256: 1f18e3b0c19b051ba44175fcce06111fb4183956892ce0571decce29a01f2656
  original_relations_sha256: e9e3541754c35bcb0bf874946b6cad2c9b585cdfd84588593037ece588a2881a
---
## Summary

Apply the requested Direct Atom Update

## Claim scope

One bound non-container Atom within [Atom Lifecycle_Update Atom Directly](../CA-O-10023-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom-directly.md).

## Claim

### Kind

Execution.

### Inputs

Selected Atom; requested changes; `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Apply one Direct Atom Update](../CA-O-10000-PROJECT_CONFIGURATION-ACTION--apply-one-direct-atom-update.md).

### Outputs

The called Action's declared Outputs.
