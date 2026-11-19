---
identity:
  atom_id: CA-O-10012
  ref_id: CA-O-10012
context:
  container:
    atom: CA-O-10016
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
  - CA-O-10002
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10012-PROJECT_CONFIGURATION-STEP--check-draft-input.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10012-PROJECT_CONFIGURATION-STEP--check-draft-input.md
  source_atom_id: CA-O-10012
  source_atom_revision: 1
  source_sha256: c2249b10fd272f0d340f8579539bc2c48b3f9468fb34226c9c0c857b59f778bd
  original_relations_sha256: 5e468acf8860f9851b5066a6fa98855a8c67ed1e07b7c01dfa1cab1a534a58d9
---
## Summary

Check Draft input

## Claim scope

One accumulated Draft request from [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md).

## Claim

### Kind

Decision.

### Inputs

Accumulated `parameters` and `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Check Draft input formats and allowed values](../CA-O-10002-PROJECT_CONFIGURATION-ACTION--check-draft-input-formats-and-allowed-values.md).

### Outputs

`parameters`, `requested_input`, and warnings returned by the called Action.
