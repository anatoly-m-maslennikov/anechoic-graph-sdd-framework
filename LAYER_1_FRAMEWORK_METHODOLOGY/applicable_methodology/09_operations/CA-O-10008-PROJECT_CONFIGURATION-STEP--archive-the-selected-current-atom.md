---
identity:
  atom_id: CA-O-10008
  ref_id: CA-O-10008
context:
  container:
    atom: CA-O-10009
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
  - CA-O-10001
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10008-PROJECT_CONFIGURATION-STEP--archive-the-selected-current-atom.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom/CA-O-10008-PROJECT_CONFIGURATION-STEP--archive-the-selected-current-atom.md
  source_atom_id: CA-O-10008
  source_atom_revision: 1
  source_sha256: 7bacf4dd4f7fde221cc813b76a4d332bd3a8a5bf210597e64885521ed2d35ec1
  original_relations_sha256: de7c1b6664b0d45394bf85b647eeeb3ff4222ce26b308fa109052a8959849388
---
## Summary

Archive the selected Current Atom

## Claim scope

One exact Current Atom binding within [Atom Lifecycle_Archive Atom](../CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom.md).

## Claim

### Kind

Execution.

### Inputs

Selected source, `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Archive one Current Atom](../CA-O-10001-PROJECT_CONFIGURATION-ACTION--archive-one-current-atom.md).

### Outputs

The called Action's declared Outputs.
