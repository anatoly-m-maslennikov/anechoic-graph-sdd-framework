---
atom_id: CA-R-2561
ref_id: CA-R-2561
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Node.**
tier: 3
status: Active
version: 2
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-2561-CORE_META_MODEL-RULE--require-scalar-property-immutability.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2561-CORE_META_MODEL-CFEL--require-scalar-immutability.md
  source_atom_id: CA-R-2561
  source_atom_revision: 2
  source_sha256: 35ab93640a08fe6283bb8557615bbfd99df94a4704cf45f7b4d0c7dcd90d1991
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Require scalar Property immutability

## Claim

### Prose Claim


Property immutability requires the same valid scalar Property value for one logical bearer from the first point when the surrounding scope selects that Property onward.

- At first applicability, bind the one existing valid scalar value. Existing occurrence, Format and value-cardinality constraints still apply. Guard an optional Property before enabling its immutability check.
- Bind later versions to the same logical bearer using supplied lineage, not by matching the mutable Property value. A new Version or Carrier representation does not create a new bearer for this check.
- If a condition activates immutability, the constraint remains active for that bearer after the first true condition, including when later versions no longer satisfy the guard.
- Use the first applicable value, not the latest observed value. Missing or invalid required values, unresolved bearer lineage, or incomplete history needed to establish the first applicable value are errors; none proves immutability.
- After activation, every later version of that bearer must still provide exactly one valid scalar value matching the bound value. A later false guard or removal of an optional Property does not suspend the constraint. Compare using the declared scalar Format, without implicit normalization or coercion.

Apply immutability as a read-only invariant.
