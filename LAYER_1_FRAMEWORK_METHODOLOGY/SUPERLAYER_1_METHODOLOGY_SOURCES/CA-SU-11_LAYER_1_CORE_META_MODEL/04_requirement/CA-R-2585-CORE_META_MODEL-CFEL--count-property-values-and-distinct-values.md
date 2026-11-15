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
---
## Summary

Count direct Property values and distinct values

## Claim

### Prose Claim

- A direct-value count measures the actual values of one Property on one bearer. Equal values contribute separate occurrences. An absent optional Property contributes zero.
- A distinct-value count compares values using their declared Format. Compare references by resolved identity. Count dependent Property names separately.
- Report an error when the bearer, Property or value cannot be resolved.
