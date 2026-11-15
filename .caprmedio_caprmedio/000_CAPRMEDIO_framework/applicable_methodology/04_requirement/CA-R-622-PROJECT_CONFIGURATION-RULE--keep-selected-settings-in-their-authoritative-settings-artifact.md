---
atom_id: CA-R-622
ref_id: CA-R-622
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Project.Settings
  dependencies:
  - CAPRMEDIO_MODEL <+ Project
  - CAPRMEDIO_MODEL <+ Project.Settings
  - CAPRMEDIO_MODEL <+ Term//Artifact
  - CAPRMEDIO_MODEL <+ Atom
  - "CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection"
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
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
llm_session_ids:
- codex:019f591f-04f6-70f2-8de7-828b7cccc69d
- codex:01a02650-eff7-7453-8c37-0699b36773c6
cce_version: cce_1
cce_form: obligation
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: caprmedio
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-622-PROJECT_CONFIGURATION-RULE--keep-selected-settings-in-their-authoritative-settings-artifact.md
  source_atom_id: CA-R-622
  source_atom_revision: 37
  source_sha256: d6db640196314ed56b74382ac51c08be6afc9a33daf662b088b6c6cb1648d40d
  original_relations_sha256: 78706cde4a3ba914563fe339a8473dd2a80658662fbddfbfba8f1ce168f57b31
---
## Summary
Keep selected settings in their authoritative Settings Artifact

## Claim

### Prose Claim


the CAPRMEDIO Framework Instance serving caprmedio **must** consume Project Settings according **to** Core Meta-Model authority under CA-R-2748, **without** redefining their purpose, locations, **or** selected values **in** Project Atoms.
