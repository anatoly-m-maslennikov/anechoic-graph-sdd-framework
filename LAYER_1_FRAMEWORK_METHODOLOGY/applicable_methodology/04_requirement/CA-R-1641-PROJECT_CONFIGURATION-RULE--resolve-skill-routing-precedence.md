---
atom_id: CA-R-1641
ref_id: CA-R-1641
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Entity/Object/Continuant/Governing Objects/Governing Configuration
  dependencies:
  - ANECHOIC_STRUCTURE <+ Aspects <+ UX <+ Entry
  - "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization"
  - ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
tier: 3
status: Active
version: 33
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1641-PROJECT_CONFIGURATION-RULE--resolve-skill-routing-precedence.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1641-PROJECT_CONFIGURATION-RULE--resolve-skill-routing-precedence.md
  source_atom_id: CA-R-1641
  source_atom_revision: 33
  source_sha256: f9c99228d830d3f6722fe25fcf36fe27db2be2dc0feb8be26c10c8109b658069
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary
Resolve skill routing precedence

## Claim

### Prose Claim

skill route resolution.


skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
