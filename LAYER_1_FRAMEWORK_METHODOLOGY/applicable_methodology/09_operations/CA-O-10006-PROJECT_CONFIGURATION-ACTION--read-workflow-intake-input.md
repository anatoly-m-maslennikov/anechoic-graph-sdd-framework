---
identity:
  atom_id: CA-O-10006
  ref_id: CA-O-10006
context:
  container:
    scope_unit: CA-SU-13
  role: Operations
  form: Action
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/Action
    dependencies:
    - ANECHOIC_MODEL <+ Atom
    - ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
  tier: 3
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10006-PROJECT_CONFIGURATION-ACTION--read-workflow-intake-input.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10006-PROJECT_CONFIGURATION-ACTION--read-workflow-intake-input.md
  source_atom_id: CA-O-10006
  source_atom_revision: 1
  source_sha256: 6f09545d122bc0f82af27019a674bfe488dda1ac1ff4ea9382f497ded2bc8661
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Read Workflow intake input

## Claim scope

One bound Workflow Run and its MCP intake dictionary.

## Claim

### Inputs

The bound Project, Workflow Run, request and MCP intake dictionary.

### Fixed parameters

None.

### Effect

At MCP entry, read the dictionary bound to the Project Run and invocation; when called by a Workflow, read its actual caller-bound dictionary, never the parent MCP query. Validate only that binding and the dictionary envelope. Do not infer, supplement, validate fields or mutate a carrier.

### Outputs

Return the dictionary unchanged. Return an explicit failure if the binding or dictionary envelope is invalid.
