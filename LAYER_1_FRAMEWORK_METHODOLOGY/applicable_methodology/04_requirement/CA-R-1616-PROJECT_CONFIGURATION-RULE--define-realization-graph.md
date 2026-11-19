---
atom_id: CA-R-1616
ref_id: CA-R-1616
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Projection/(.Form := Realization Graph)
  dependencies:
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Traceability
  - ANECHOIC_MODEL <+ Entity
  - 'ANECHOIC_MODEL <+ Entity/Object/Continuant/Projection/Type: Realization Graph'
  - ANECHOIC_MODEL <+ Journal
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Relation
tier: 3
status: Active
version: 25
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1616-PROJECT_CONFIGURATION-RULE--define-realization-graph.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1616-PROJECT_CONFIGURATION-RULE--define-realization-graph.md
  source_atom_id: CA-R-1616
  source_atom_revision: 25
  source_sha256: e9e8c7e00fbeffe88788637c273ca7d04e307af7cfcb4dbda601c4d7d08812ac
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Realization Graph

## Claim

### Prose Claim


Realization Graphs derived from a declared selection of existing Implementation sources and available evidence.


Realization Graph **means** a non-authoritative Projection of Entities **and** typed Relations derived from a declared selection of existing Implementation sources **and** available evidence, used **to** understand that Implementation **and** support reverse engineering into proposed RMED.

- the Projection **must** retain source traceability under CA-R-2535 **and** generation identity under CA-R-1493, using **only** the source kinds selected for the job; legacy Implementation need **not** have pre-existing RMED **or** Journal records.
- missing evidence **and** uncertain interpretations **must** be reported. observed structure **or** behavior does **not** establish intended Requirements, a passed Evaluation, **or** completeness outside the checked selection.
- the Artifact kind remains Projection, including **when** delivered as an Implementation output under CA-R-1568. views derive from its source-backed facts **without** creating another source of truth.
