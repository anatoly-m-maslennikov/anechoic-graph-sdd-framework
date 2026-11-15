---
identity:
  atom_id: CA-O-10019
  ref_id: CA-O-10019
context:
  container:
    atom: CA-O-10024
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
  - CA-O-10009
state:
  status: Active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10019-PROJECT_CONFIGURATION-STEP--archive-the-exact-current-version.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10024-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10024-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom/CA-O-10019-PROJECT_CONFIGURATION-STEP--archive-the-exact-current-version.md
  source_atom_id: CA-O-10019
  source_atom_revision: 1
  source_sha256: 0e7834273bf95f84fcf31840e5b23fe5562d9cffadf644cfd4f724274c2ce6e1
  original_relations_sha256: 115d98ea9034064933c1fa7e2927f620832d03a6ce7dfb7ec28cc45693b28e27
---
## Summary

Archive the exact Current Version

## Claim scope

One bound exact Current source within [Atom Lifecycle_Update Atom](../CA-O-10024-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom.md).

## Claim

### Kind

Execution.

### Inputs

Bind the original `sourceCurrent`, `projectContext` to the called Workflow. `targetStatus` remains enclosing-Workflow context.

### Fixed parameters

None.

### Runs

The Workflow [Atom Lifecycle_Archive Atom](../CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom.md).

### Outputs

The called Workflow's declared Output.
