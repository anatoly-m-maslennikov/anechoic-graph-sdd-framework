---
atom_id: CA-R-2552
ref_id: CA-R-2552@5-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Node
tier: 3
status: Draft
version: 5
updated_at: "2026-11-06 19:37:39 +0400"
carrier_destination:
  file:
    name: CA-R-2552@5-draft-RULE--bind-instance-variables.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Bind instance variables

## Claim

### Prose Claim

- Validate against a fully resolved population of the declared kind and its narrower kinds. Count each logical object once, even when several Carriers refer to it.
- Apply Property occurrence bounds separately to each effective Property and bearer. Inherited Properties retain their Declaration identity. A structural Property can hold declared dependents with zero direct values.
- Bind a Python reference to the same object throughout each check. Test object identity and existing links using the supplied Project data. A scoped test applies its condition only to the matching bindings.
- Relation endpoint counts apply per endpoint. Check missing or ambiguous object and Property bindings as errors.
