---
atom_id: CA-D-307
ref_id: CA-D-307
container:
  scope_unit: CA-SU-13
role: Delivery
form: Decision
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection/(.Form:=Applicable Methodology)
  dependencies:
  - CAPRMEDIO_MODEL <+ Relation//GOVERNS
  - CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics.Dependencies
tier: 3
status: Active
version: 28
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-D-307-PROJECT_CONFIGURATION-DECISION--prohibit-persistent-applicable-methodology-subject-indexes.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery/CA-D-307-PROJECT_CONFIGURATION-DECISION--prohibit-persistent-applicable-methodology-subject-indexes.md
  source_atom_id: CA-D-307
  source_atom_revision: 28
  source_sha256: 1effe422b207b17df22020c73a6ed260e2ab22d354c0a6538829db98b0bd6218
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Prohibit Persistent Applicable Methodology Subject Indexes

## Claim

### Prose Claim


Applicable Methodology.


Applicable Methodology **must not** store a persistent GOVERNS **or** DEPENDS_ON Subject Index Carrier.
