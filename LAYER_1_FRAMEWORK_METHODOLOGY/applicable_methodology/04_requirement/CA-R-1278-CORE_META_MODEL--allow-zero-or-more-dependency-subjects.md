---
atom_id: CA-R-1278
ref_id: CA-R-1278
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics.Dependencies
tier: 2
status: Active
version: 23
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1278-CORE_META_MODEL-RULE--allow-zero-or-more-dependency-subjects.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1278-CORE_META_MODEL--allow-zero-or-more-dependency-subjects.md
  source_atom_id: CA-R-1278
  source_atom_revision: 23
  source_sha256: ddd054dbc0066ea1b72235c3381a17f59ca5eaedfe6834f18019b1da37b123a0
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Allow Zero or More Dependency Subjects

## Claim

### Prose Claim


direct DEPENDS_ON targets in an Atom's Subjects Property.


**every** Atom **may** declare **`>=0`** distinct direct DEPENDS_ON targets **in** its Subjects Property.
