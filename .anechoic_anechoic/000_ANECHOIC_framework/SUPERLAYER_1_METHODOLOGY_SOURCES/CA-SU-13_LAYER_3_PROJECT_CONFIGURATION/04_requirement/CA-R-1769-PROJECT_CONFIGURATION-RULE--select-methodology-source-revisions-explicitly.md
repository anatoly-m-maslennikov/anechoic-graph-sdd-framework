---
atom_id: CA-R-1769
ref_id: CA-R-1769
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data
    Handling <+ Source Selection
  dependencies:
  - ANECHOIC_MODEL <+ Node/Continuant
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/History
tier: 2
relations:
  child_of:
  - CA-M-538
status: Active
version: 37
updated_at: 2026-11-11 16:09:46 +0400
carrier_destination:
  file:
    name: CA-R-1769-PROJECT_CONFIGURATION-RULE--select-methodology-source-revisions-explicitly.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
---
## Summary

Select Methodology Source revisions explicitly

## Claim

### Prose Claim


Methodology Source updates or downgrades applied by a Project.


a Project **must** apply a Methodology Source update **or** downgrade **only** by selecting an identified source revision **and** reconciling affected Project authority; the selection **must not** silently rewrite other Methodology Sources **or** Project-owned Atoms.
