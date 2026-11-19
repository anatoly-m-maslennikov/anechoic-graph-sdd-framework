---
atom_id: CA-R-1515
ref_id: CA-R-1515
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
  dependencies:
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action)'
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow)'
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - ANECHOIC_STRUCTURE <+ Scope Unit//CORE_META_MODEL
  - ANECHOIC_STRUCTURE <+ Entity/Object/Continuant/Selection//Extension Sources
  - ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
  - "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure"
tier: 2
status: Active
version: 25
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1515-PROJECT_CONFIGURATION-RULE--keep-canonical-actions-and-workflows-in-methodology.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1515-PROJECT_CONFIGURATION-RULE--keep-canonical-actions-and-workflows-in-methodology.md
  source_atom_id: CA-R-1515
  source_atom_revision: 25
  source_sha256: fd5fa6b997c0b9157c1a9687eee498c75a9f868050d188d8945d953d646b833e
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep canonical Actions and Workflows in methodology

## Claim

### Prose Claim


the canonical O definitions of Actions and Workflows used by TOOLS in the anechoic Project.


**in** the anechoic Project, the canonical O definitions of Actions **and** Workflows used by TOOLS **must** belong **to** methodology source Scope Units.

## Details

- a Tool references the applicable canonical definition rather than independently defining the same Action **or** Workflow **in** its own Scope Unit.
- the owning methodology source **may** be Core Meta-Model, an admitted Extension, **or** Project Configuration according **to** the definition's actual applicability; this allocation rule does **not** make project-specific behavior universal Core authority.
- Implementation code **and** prompts **may** realize the definition **without** becoming another independently maintained operational definition.
