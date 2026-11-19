---
atom_id: CA-R-1292
ref_id: CA-R-1292
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Scope Unit
  dependencies:
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Goal)'
  - ANECHOIC_MODEL <+ Atom.Content
tier: 1
status: Active
version: 31
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1292-CORE_META_MODEL-RULE--require-an-accepted-goal-for-every-scope-unit.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1292-CORE_META_MODEL-RULE--require-an-accepted-goal-for-every-scope-unit.md
  source_atom_id: CA-R-1292
  source_atom_revision: 31
  source_sha256: 51749089ab6c3f020ea7086e333baad18e87eb5df18afae805f3dd8b1c750715
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Require an Accepted Goal for Every Scope Unit

## Claim

### Prose Claim


Scope Units and their Claim Target Scope Unit references.


**every** Scope Unit **must** remain the Claim Target Scope Unit of **`>=1`** accepted Goal Atom.
