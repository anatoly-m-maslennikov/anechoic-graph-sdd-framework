---
atom_id: CA-R-1651
ref_id: CA-R-1651
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form := Plan)'
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
tier: 3
relations:
  child_of:
  - CA-R-1711
status: Active
version: 33
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1651-PROJECT_CONFIGURATION-RULE--propose-development-backlog-splits.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1651-PROJECT_CONFIGURATION-RULE--propose-development-backlog-splits.md
  source_atom_id: CA-R-1651
  source_atom_revision: 33
  source_sha256: f6d86de91dd8c8c649d00bf20d63482cff1c57d67869fa3b035190b2698966d4
  original_relations_sha256: a6cede7fe831d2cd728ef1b5f22f9bdfe75c97f8f8154479b37e5d92b25350a5
---
## Summary

Propose Development Backlog splits

## Claim

### Prose Claim


a Development Backlog Epic that **contains** **`>50`** Task Atoms.


Governance **must** propose narrower ordered Epics **and** **may** apply the split **only** **after** Operator approval.
