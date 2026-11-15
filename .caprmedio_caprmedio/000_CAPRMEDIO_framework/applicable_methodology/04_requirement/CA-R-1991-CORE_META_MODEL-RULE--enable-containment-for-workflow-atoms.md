---
atom_id: CA-R-1991
ref_id: CA-R-1991
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: 'CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow).Enabled Relations.Contains'
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom.Enabled Relations.Contains
  - 'CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step)'
tier: 3
relations:
  child_of:
  - CA-R-2478
status: Active
version: 13
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1991-CORE_META_MODEL-RULE--enable-containment-for-workflow-atoms.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1991-CORE_META_MODEL-RULE--enable-containment-for-workflow-atoms.md
  source_atom_id: CA-R-1991
  source_atom_revision: 13
  source_sha256: 2fda08b0c8f54053a280af5bf8f270a8f11cee01844b394109241d6d86f9dd1e
  original_relations_sha256: 4fde62f0627e52833e954bbd64d451c404b9f9d66585c52603ef12fa5886adfa
---
## Summary

Enable containment for Workflow Atoms

## Claim

### Prose Claim


Containment capability of Workflow Atoms.


`Atom/(.Header.Role := Operations)/(.Header.Form := Workflow).Enabled Relations.Contains` **must** be True. a Workflow Atom **may** contain Step Atoms.

## Details

The Workflow remains an Atom. Its Steps retain their own definitions and Action references. This permission does not copy shared Actions into a Workflow or replace its declared control flow with folder order.
