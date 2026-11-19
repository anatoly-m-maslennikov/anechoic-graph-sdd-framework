---
atom_id: CA-R-1659
ref_id: CA-R-1659
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Relation
tier: 3
relations:
  child_of:
  - CA-R-1756
status: Active
version: 31
updated_at: 2026-11-02 19:44:26 +0400
carrier_destination:
  file:
    name: CA-R-1659-CORE_META_MODEL-RULE--derive-inverse-structural-ownership.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1659-CORE_META_MODEL-RULE--derive-inverse-structural-ownership.md
  source_atom_id: CA-R-1659
  source_atom_revision: 31
  source_sha256: 411dbf7219290128b3789291074d2d73ce60864d407032a0c513e2b486af3a4c
  original_relations_sha256: 7f6ad774f4a8dbcb06ed291239fe4f8c20c3c04d6c9490bdc10c6fb2680d87fd
---
## Summary

Derive inverse structural ownership

## Claim

### Prose Claim


the inverse `structural_children` view derived from stored `structural_parent` relations.


ANECHOIC **must** derive the inverse `structural_children` view from stored `structural_parent` relations **and** **must not** persist that inverse separately.
