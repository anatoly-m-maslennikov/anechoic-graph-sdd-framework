---
atom_id: CA-R-2585
ref_id: CA-R-2585
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Node.**
tier: 3
status: Active
version: 2
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-2585-CORE_META_MODEL-RULE--count-direct-property-values-and-distinct-values.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2585-CORE_META_MODEL-CFEL--count-property-values-and-distinct-values.md
  source_atom_id: CA-R-2585
  source_atom_revision: 2
  source_sha256: ffb5a23d2156216a48b1d87c08cea402f6d918b0599e3cbc25a35f104d97ae98
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Count direct Property values and distinct values

## Claim

### Prose Claim

- A direct-value count measures the actual values of one Property on one bearer. Equal values contribute separate occurrences. An absent optional Property contributes zero.
- A distinct-value count compares values using their declared Format. Compare references by resolved identity. Count dependent Property names separately.
- Report an error when the bearer, Property or value cannot be resolved.
