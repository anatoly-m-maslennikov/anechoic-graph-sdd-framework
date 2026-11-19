---
atom_id: CA-R-1772
ref_id: CA-R-1772
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Project
  dependencies:
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)
  - ANECHOIC_MODEL <+ Package/Project Package
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_STRUCTURE <+ Aspects <+ Product
tier: 1
relations:
  child_of:
  - CA-R-3025
status: Active
version: 39
updated_at: "2026-11-11 18:46:16 +0400"
carrier_destination:
  file:
    name: CA-R-1772-CORE_META_MODEL-RULE--minimal-default-project-model.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1772-CORE_META_MODEL-RULE--minimal-default-project-model.md
  source_atom_id: CA-R-1772
  source_atom_revision: 39
  source_sha256: aa6a339040128419003fa68bc95c392eefe8c0836544645446da1edd8d62a48d
  original_relations_sha256: 8c280c20b628a0311b96d72405c9b8e250a61adb2e9a1c9ccf8dc1d28e7d13b5
---
## Summary

Minimal default project model

## Claim

### Prose Claim


Project models.


ANECHOIC **must** use Project-scope Requirement authority plus its real Implementation as the minimum Project model, **must not** require an Implementation Atom, **and** **may** enable other Atom roles, applicability tiers, descendant scopes, **or** automation **only** **when** necessary. Scope Unit ancestry remains parent-declaration data; no Structural Level property is required.
