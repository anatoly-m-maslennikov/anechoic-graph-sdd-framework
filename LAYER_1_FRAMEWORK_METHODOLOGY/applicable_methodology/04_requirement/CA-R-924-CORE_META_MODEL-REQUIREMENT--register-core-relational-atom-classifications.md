---
atom_id: CA-R-924
ref_id: CA-R-924
container:
  scope_unit: CA-SU-11
role: Requirement
form: Requirement
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Form
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Goal)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Demand)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form := Plan)
tier: 4
relations:
  child_of:
  - CA-R-923
status: Active
version: 39
updated_at: "2026-11-07 15:18:44 +0400"
carrier_destination:
  file:
    name: CA-R-924-CORE_META_MODEL-REQUIREMENT--register-core-relational-atom-classifications.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-924-CORE_META_MODEL-REQUIREMENT--register-core-relational-atom-classifications.md
  source_atom_id: CA-R-924
  source_atom_revision: 39
  source_sha256: 0f7d4c12a3a0ed5c8dd5ed3f3c269a7ec67a24a2789045b722e53b0af660a849
  original_relations_sha256: a04b2740365697ee3e4186cfbec88741d45af9b261c1a52f42e455a9e0171e3d
---

## Summary

Register Core Relational Atom Classifications

## Claim

### Prose Claim

The allowed qualified Relational Atom types in the Core Model include Requirement/Goal, Requirement/Demand, Plan/Plan, and Requirement/Scope Delegation, Method/Scope Delegation, Evaluation/Scope Delegation, Delivery/Scope Delegation and Operations/Scope Delegation.

A Scope Delegation is relational because its receiving Scope Unit differs from its direct containing Scope Unit. A Plan is relational only when its actual Claim target differs under the Relational Atom definition, not because it has decomposition, blocking or a particular Label.
