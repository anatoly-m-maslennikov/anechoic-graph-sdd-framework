---
atom_id: CA-R-1722
ref_id: CA-R-1722
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Scope Unit
  dependencies:
  - ANECHOIC_STRUCTURE <+ Scope Unit//METHODOLOGY_SOURCES
  - ANECHOIC_STRUCTURE <+ Scope Unit//CORE_META_MODEL
  - ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
tier: 1
relations:
  child_of:
  - CA-R-3048
status: Active
version: 33
updated_at: 2026-11-11 16:16:08 +0400
carrier_destination:
  file:
    name: CA-R-1722-CORE_META_MODEL--govern-extension-semantics.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1722-CORE_META_MODEL--govern-extension-semantics.md
  source_atom_id: CA-R-1722
  source_atom_revision: 33
  source_sha256: a3c12f39f757052432d44691c7ffa4ff4d3b5e8098545e7ce7ca9cc459f0f3ab
  original_relations_sha256: d035597e76f458c418413a53cb546b17afb2dacad56cc63d30879d5bb88356aa
---
## Summary

Govern extension semantics

## Claim

### Prose Claim


Extension semantics within the Core Meta-Model.


an Extension **must** provide a reusable, independently governed, optional package of capability contributions. its authority **and** evolution remain distinct from Core Meta-Model **and** Project Configuration authority.

## Details

this packaging requirement does **not** establish another Entity classification: the Extension definition **and** its permitted expansion boundary remain governed by CA-R-1217.
