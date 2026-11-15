---
atom_id: CA-R-2566
ref_id: CA-R-2566
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Node
tier: 3
status: Active
version: 2
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-2566-CORE_META_MODEL-RULE--filter-instances-and-select-maximum-values.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2566-CORE_META_MODEL-CFEL--filter-instances-and-select-maximum-values.md
  source_atom_id: CA-R-2566
  source_atom_revision: 2
  source_sha256: ecc62404c3785fcbd5bb0b0baeae89ab1bc767777065fc8f33aa709f179eae25
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Filter instances and select maximum values

## Claim

### Prose Claim


- Select matching instances of the declared kind and its narrower kinds from an explicit Project snapshot.
- Evaluate predicates on each candidate, with Python's short-circuit rules. Resolve references to their target identity. An evaluated predicate with a missing, invalid or unresolved value raises an error.
- Each matching instance contributes one valid scalar. Return the greatest scalar under the applicable Format. Compare datetimes by instant.
- Reject empty, incomplete or incompatible input. Selection and comparison are read-only.
