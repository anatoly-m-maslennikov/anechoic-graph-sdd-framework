---
atom_id: CA-R-1772
ref_id: CA-R-1772@37
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Project
  dependencies:
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Requirement)
  - ANECHOIC_MODEL <+ Package/Implementation
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_STRUCTURE <+ Aspects <+ Product
tier: 1
relations:
  child_of:
  - CA-M-005
status: Archived
version: 37
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1772@37-CORE_META_MODEL-RULE--minimal-default-project-model.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/archive
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Minimal default project model

## Claim

### Prose Claim


Project models.


ANECHOIC **must** use Project-scope Requirement authority plus its real Implementation as the minimum Project model, **must not** require an Implementation Atom, **and** **may** enable other Atom roles, applicability tiers, descendant scopes, **or** automation **only** **when** necessary. Scope Unit ancestry remains parent-declaration data; no Structural Level property is required.
