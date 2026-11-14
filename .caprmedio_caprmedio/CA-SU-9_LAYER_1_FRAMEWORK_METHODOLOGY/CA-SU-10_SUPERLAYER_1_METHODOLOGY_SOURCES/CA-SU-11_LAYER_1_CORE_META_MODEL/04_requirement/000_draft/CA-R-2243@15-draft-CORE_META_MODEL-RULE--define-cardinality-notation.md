---
atom_id: CA-R-2243
ref_id: CA-R-2243@15-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Cardinality
tier: 1
status: draft
version: 15
updated_at: '2026-11-12T18:31:37.011484+00:00'
carrier_destination:
  file:
    name: CA-R-2243@15-draft-CORE_META_MODEL-RULE--define-cardinality-notation.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---

## Summary

Define Cardinality Notation

## Claim

### Prose Claim

- Allowed bounds use non-negative integers. Both ends of a range are inclusive.
- Each declared named Property occurs at most once per bearer. An explicit occurrence bound governs presence. Without it, a positive direct-value minimum requires a leaf Property. A zero minimum leaves presence optional.
- Direct-value counts measure values on one occurrence. A structural Property can have dependents and zero direct values.
- A dependent Property count measures distinct selected names on the bearer. An immediate count includes one level. A recursive count includes all selected descendants.
- Each Relation endpoint has an independent count of matching links per selected endpoint. The inverse swaps the two counts.
- An omitted count is unspecified. A comparison tests the actual count separately from the allowed bound.
