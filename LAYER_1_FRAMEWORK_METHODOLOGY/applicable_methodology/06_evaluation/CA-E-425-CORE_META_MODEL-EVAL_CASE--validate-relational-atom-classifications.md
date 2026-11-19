---
atom_id: CA-E-425
ref_id: CA-E-425
container:
  scope_unit: CA-SU-11
role: Evaluation
form: Eval Case
topics:
  main_subject: ANECHOIC_MODEL <+ Atom
  dependencies:
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Goal)'
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Demand)'
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
tier: 5
relations:
  evaluation_for:
  - CA-R-923
  - CA-R-924
  - CA-R-1576@21
  - CA-R-1588
status: Active
version: 30
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-E-425-CORE_META_MODEL-EVAL_CASE--validate-relational-atom-classifications.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/CA-E-425-CORE_META_MODEL-EVAL_CASE--validate-relational-atom-classifications.md
  source_atom_id: CA-E-425
  source_atom_revision: 30
  source_sha256: 6e7b15c83bba56394625854ef0657f9c65ed643fbbd3a712fd9f914352288478
  original_relations_sha256: f51298c27d48a0f3abb1efc6b55cfe7af6ae821371edecacd6a64bf78acd5f9e
---
## Summary

Validate Relational Atom Classifications

## Claim

### Prose Claim


Relational Atom classifications.


the Relational Atom classification Evaluation **must** enforce the qualified Types admitted by CA-R-924 **without** treating Plan Labels as Types.

- accept permitted relational Requirement/Goal, Requirement/Demand, **and** Plan/Plan cases with explicit non-default Claim targets.
- accept a current-scope Plan with decomposition **or** blocking **without** classifying it as relational merely because those Relations exist.
- change the Plan Label from Task **to** Objective **or** Epic; retain the same target-based classification.
- reject an unregistered qualified Type, an invalid relational target, **or** a Label interpreted as Type authority.

report the exact Atom, qualified Type, **and** target condition.
