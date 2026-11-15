---
atom_id: CA-R-1642
ref_id: CA-R-1642
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Carrier
  dependencies:
  - CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+
    Data Transformation
tier: 3
status: Active
version: 33
updated_at: 2026-11-02 19:44:26 +0400
carrier_destination:
  file:
    name: CA-R-1642-PROJECT_CONFIGURATION-RULE--register-generated-data-stages.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1642-PROJECT_CONFIGURATION-RULE--register-generated-data-stages.md
  source_atom_id: CA-R-1642
  source_atom_revision: 33
  source_sha256: 663c9405d065ae4b3291fd4b398fd13d2c70b5d146a1abf68d09a0e5d534f2db
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register generated-data stages

## Claim

### Prose Claim


the ordered generated-data pipeline stages.


the following ordered generated-data pipeline stages **must** be registered, referenced by their Carrier prefixes governed by CA-D-388-PROJECT_CONFIGURATION-ENG_DECISION--serialize-generated-data-stage-prefixes-and-formats:

| Stage reference | Stage meaning |
| --- | --- |
| `src` | canonical Journal input; authority comes from the Journal, **not** the prefix. |
| `stg` | deterministic, lossless Projection of a bounded `src` frontier. |
| `mrt` | consumer-ready semantic Projection, including Requirement groupings by scope **and** tier **or** Mermaid relation maps. |
| `biz` | aggregated CAPRMEDIO artifact **and** implementation metrics, including point-in-time snapshots **and** historical trends. |

dependencies **must** move forward through `src → stg → mrt → biz`; a stage **may** depend on **any** earlier registered stage but **must not** depend on a later stage.
