---
identity:
  atom_id: CA-O-10003
  ref_id: CA-O-10003
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
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
destination:
  file:
    name: CA-O-10003-PROJECT_CONFIGURATION-ACTION--create-one-atom-draft.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-10003-PROJECT_CONFIGURATION-ACTION--create-one-atom-draft.md
  source_atom_id: CA-O-10003
  source_atom_revision: 1
  source_sha256: 8657c1fbc75e189810e1b19bae2e3f7e0d242744fde59f672737e4817a940fcb
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Create one Atom Draft

## Claim scope

One non-container Draft materialization under its applicable model.

## Claim

Create a Draft from `newAtom` properties or from a selected existing Atom and supplied property changes. For an existing Atom read its full properties and content, merge supplied properties, and carry all others forward. Derive Draft metadata, filename and path from the resulting properties and model; the caller does not provide a filename or path. A supplied Scope Unit is a logical property and determines derived placement under the destination Scope Unit. For a Current source with unchanged Summary and Content Role, assign the same-ID Draft Version N+1 once; promotion retains it without another increment. If Summary or Content Role changes, the result is a new identity promoted at Version 1. Editing an existing Draft in place preserves its Version and Updated At. Check formats and allowed values without a semantic gate. On missing or invalid input provide a short explanation and request an additional input dictionary; wait for it. Report an effect failure explicitly. Journal business observations are independent and nonblocking.

### Outputs

`savedDraft`, a request for additional input, or an explicit failure; any Journal warning is separate.
