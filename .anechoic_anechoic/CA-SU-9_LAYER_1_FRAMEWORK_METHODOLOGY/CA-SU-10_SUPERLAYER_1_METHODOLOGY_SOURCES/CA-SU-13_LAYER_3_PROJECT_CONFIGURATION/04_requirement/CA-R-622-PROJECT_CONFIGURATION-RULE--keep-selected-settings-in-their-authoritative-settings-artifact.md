---
atom_id: CA-R-622
ref_id: CA-R-622
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Project.Settings
  dependencies:
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Project.Settings
  - ANECHOIC_MODEL <+ Term//Artifact
  - ANECHOIC_MODEL <+ Atom
  - "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection"
tier: 1
relations:
  child_of:
  - CA-R-3033
status: Active
version: 37
updated_at: "2026-11-11 18:46:16 +0400"
carrier_destination:
  file:
    name: CA-R-622-PROJECT_CONFIGURATION-RULE--keep-selected-settings-in-their-authoritative-settings-artifact.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
llm_session_ids:
- codex:019f591f-04f6-70f2-8de7-828b7cccc69d
- codex:01a02650-eff7-7453-8c37-0699b36773c6
cce_version: cce_1
cce_form: obligation
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: anechoic
---
## Summary
Keep selected settings in their authoritative Settings Artifact

## Claim

### Prose Claim


the ANECHOIC Framework Instance serving anechoic **must** consume Project Settings according **to** Core Meta-Model authority under CA-R-2748, **without** redefining their purpose, locations, **or** selected values **in** Project Atoms.
