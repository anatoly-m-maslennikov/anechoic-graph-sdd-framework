---
atom_id: CA-R-1557
ref_id: CA-R-1557
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/AI Agent
  dependencies:
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/AI Agent
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/AI Agent.Permissions
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Concern)
tier: 2
relations:
  child_of:
  - CA-R-1702
status: Active
version: 21
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1557-CORE_META_MODEL-RULE--keep-conflict-discovery-in-exploration-mode.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1557-CORE_META_MODEL-RULE--keep-conflict-discovery-in-exploration-mode.md
  source_atom_id: CA-R-1557
  source_atom_revision: 21
  source_sha256: 8464e71c5369b629cc3aeb2f9f9effc954b474c5bfe8d928fde8da2207f81462
  original_relations_sha256: 86f48d79fbbfe66ffab2b0bb686a446bbbe206535c96d6e0d3b25f21670f9677
---
## Summary

Keep conflict discovery in Exploration Mode

## Claim

### Prose Claim


AI Agent discovery of conflicts in Exploration Mode.


an AI Agent **must** keep a discovered conflict **in** Exploration Mode; it **may** create a Concern for that conflict **only** **when** the Operator requests persistence **or** defers its resolution.
