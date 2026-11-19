---
identity:
  atom_id: CA-O-10014
  ref_id: CA-O-10014
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
  - CA-O-10006
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10014-PROJECT_CONFIGURATION-STEP--read-workflow-input.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10014-PROJECT_CONFIGURATION-STEP--read-workflow-input.md
  source_atom_id: CA-O-10014
  source_atom_revision: 1
  source_sha256: 37fac187e678423cb23b46decb8d4b91fac2e3414dab0008114a17719235227f
  original_relations_sha256: 6390bca3dd4a6bd987611162599e45fb701d4af032d825cf3357eec46c0b04e0
---
## Summary

Read Workflow input

## Claim scope

One root or nested invocation of [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md) and its input dictionary.

## Claim

### Kind

Input.

### Inputs

The invocation dictionary declared by the called Action; `projectContext`; the bound Workflow Run and request.

### Fixed parameters

None.

### Runs

The Action [Read Workflow intake input](../CA-O-10006-PROJECT_CONFIGURATION-ACTION--read-workflow-intake-input.md).

### Outputs

Bind the returned invocation dictionary to `parameters`.
