---
atom_id: CA-R-1428
ref_id: CA-R-1428
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Decision Confidence"
  dependencies:
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role: Plan)/(.Header.Context.Form: Plan)'
  - ANECHOIC_MODEL <+ Term//Property
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings
tier: 2
relations:
  child_of:
  - CA-R-1427@17
status: Active
version: 32
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1428-CORE_META_MODEL-RULE--permit-confidence-threshold-defaults-and-overrides.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1428-CORE_META_MODEL--permit-confidence-threshold-defaults-and-overrides.md
  source_atom_id: CA-R-1428
  source_atom_revision: 32
  source_sha256: 6334a2892fb41ff2c83d3190154e16f4ce5af921ef1cebd98c76d62bb29f3fe4
  original_relations_sha256: 78c49a17234bcda360b37449773c5ac549d056fc653111f6644e9b5c453d7e0b
---
## Summary

Permit confidence-threshold defaults and overrides

## Claim

### Prose Claim


the source of a Confidence Threshold value.


a Confidence Threshold **must** take its value from applicable direct Operator input, an explicit Property on the current Plan, the nearest enclosing Hub Plan with an explicit Property, **or** the Framework Instance Settings default; the Plan-containment chain follows `IS_CONTAINED_BY` toward the nearest enclosing Plan, **not** Label spelling.
