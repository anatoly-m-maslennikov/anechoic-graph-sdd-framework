---
atom_id: CA-R-2243
ref_id: CA-R-2243@13-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Cardinality
tier: 1
status: Draft
version: 13
updated_at: 2026-11-05 00:49:39 +0400
carrier_destination:
  file:
    name: CA-R-2243@13-draft-RULE--define-cardinality-notation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---

## Summary

Define Cardinality Notation

## Claim

### Prose Claim

- Allowed bounds use non-negative integers. Both ends of a range are inclusive.
- Each declared named Property occurs at most once per bearer. A positive applicable direct-value minimum requires a leaf Property. A zero minimum leaves presence optional. Apply explicit occurrence bounds as well.
- Direct-value counts measure values on one occurrence. A structural Property can have dependents and zero direct values.
- A dependent Property count measures distinct selected names on the bearer. An immediate count includes one level. A recursive count includes all selected descendants.
- Each Relation endpoint has an independent count of matching links per selected endpoint. The inverse swaps the two counts.
- An omitted count is unspecified. A comparison tests the actual count separately from the allowed bound.
