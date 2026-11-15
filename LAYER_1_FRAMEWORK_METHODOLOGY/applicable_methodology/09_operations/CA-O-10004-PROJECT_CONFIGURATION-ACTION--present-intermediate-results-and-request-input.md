---
identity:
  atom_id: CA-O-10004
  ref_id: CA-O-10004
context:
  container:
    scope_unit: CA-SU-13
  role: Operations
  form: Action
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/Action
    dependencies:
    - CAPRMEDIO_MODEL <+ Atom
    - CAPRMEDIO_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
  tier: 3
state:
  status: Active
  version: 4
  updated_at: '2026-11-11 17:36:30 +0400'
destination:
  file:
    name: CA-O-10004-PROJECT_CONFIGURATION-ACTION--present-intermediate-results-and-request-input.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10004-PROJECT_CONFIGURATION-ACTION--present-intermediate-results-and-request-input.md
  source_atom_id: CA-O-10004
  source_atom_revision: 4
  source_sha256: 539a25b2ac7eec1df2e7ec6e0c6253e45fe4fa2d8ff06d6edc9d8d36276a1987
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Present intermediate results and request input

## Claim scope

One bound Workflow Run that needs additional input before its current Step can continue.

## Claim

### Inputs

The bound Project, Workflow Run and current Step; intermediate results; separate warnings; and a `requested_input` dictionary. It may carry checker field entries or a broader request for additional information.

### Fixed parameters

None.

### Effect

Wait for a correction dictionary bound to the same Project, Run and Step. The caller may cancel while waiting; cancellation does not interrupt an Action. Request the missing or invalid fields through an input form in the same MCP call when the client supports it. Otherwise return the requested fields. A later MCP request for the same Tool in the same Project and client session can supply only those fields. It may also supply corrections to other inputs. Merge the supplied fields into the retained input and validate the resulting request before any effect.

### Outputs

While waiting, return intermediate results, warnings and `requested_input`; after a valid resumed call, return the correction dictionary and warnings unchanged. Report an explicit failure if the resumed binding or dictionary envelope is invalid.
