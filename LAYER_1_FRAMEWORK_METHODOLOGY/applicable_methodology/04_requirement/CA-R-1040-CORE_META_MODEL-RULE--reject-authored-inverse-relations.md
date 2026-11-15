---
atom_id: CA-R-1040
ref_id: CA-R-1040
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation
tier: 1
status: Active
version: 31
updated_at: 2026-11-02 19:44:26 +0400
carrier_destination:
  file:
    name: CA-R-1040-CORE_META_MODEL-RULE--reject-authored-inverse-relations.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1040-CORE_META_MODEL-RULE--reject-authored-inverse-relations.md
  source_atom_id: CA-R-1040
  source_atom_revision: 31
  source_sha256: 3cb0f0a9ffd12f5fc614486e086fb6ee3a4a2ff79a8db75d01068b422ef1ad6b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Reject authored inverse relations

## Claim

### Prose Claim


authored inverse typed relations.


validators **must** reject **every** inverse typed relation authored **in** an Atom Carrier.

## Details

Inverse means the derived direction declared by the governing Relation Kind definition, not a direction guessed from its name. In the containment pair, IS_CONTAINED_BY is direct from child to parent and is the only permitted authoritative direction when Atom containment is authored; CONTAINS is the inverse and must not be separately authored. This clarification does not admit a new runtime relation key or waive endpoint Entity Definition constraints.
