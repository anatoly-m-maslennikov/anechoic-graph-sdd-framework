---
atom_id: CA-R-2552
ref_id: CA-R-2552
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Node
tier: 3
status: Active
version: 4
updated_at: 2026-11-04 05:21:15 +0400
carrier_destination:
  file:
    name: CA-R-2552-CORE_META_MODEL-RULE--bind-instance-variables.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2552-CORE_META_MODEL-CFEL--bind-instance-variables.md
  source_atom_id: CA-R-2552
  source_atom_revision: 4
  source_sha256: 37ddc8b9c28f6647a96aacfdd294ded439e971da0e16568884909d962e9788cd
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Bind instance variables

## Claim

### Prose Claim

- Validate against a fully resolved population of the declared kind and its narrower kinds. Count each logical object once, even when several Carriers refer to it.
- Apply Property occurrence bounds separately to each effective Property and bearer. Inherited Properties retain their Declaration identity. A structural Property can hold declared dependents with zero direct values.
- Bind a Python reference to the same object throughout each check. Test object identity and existing links using the supplied Project data. A scoped test applies its condition only to the matching bindings.
- Relation endpoint counts apply per endpoint. Check missing or ambiguous object and Property bindings as errors.
