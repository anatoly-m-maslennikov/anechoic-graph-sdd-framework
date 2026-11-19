---
atom_id: CA-R-2472
ref_id: CA-R-2472
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Node.**
tier: 3
status: Active
version: 9
updated_at: 2026-11-04 05:21:15 +0400
carrier_destination:
  file:
    name: CA-R-2472-CORE_META_MODEL-RULE--separate-property-names-and-values.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2472-CORE_META_MODEL-RULE--separate-property-names-and-values.md
  source_atom_id: CA-R-2472
  source_atom_revision: 9
  source_sha256: d220b7ced25b8db87d866607bee5dc80855ac4f2a1b4f03495a7d64d80810e76
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Separate Property names and values

## Claim

### Prose Claim

- The complete path identifies a Property. Sibling names are unique on each
  bearer.
- Occurrence bounds govern presence. Value formats and bounds apply to the
  direct values of each occurrence. See CA-R-2327 for count semantics.
- Resolve local and inherited Declarations before checking dependent Properties.
  Only declared dependents are admitted. An applicable name selector admits
  the names and counts it declares.
- In a Subject selector, each `.*` selects one level and `.**` selects all
  descendant levels. Apply chained selectors from left to right.

