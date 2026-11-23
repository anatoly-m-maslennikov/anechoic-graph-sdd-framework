---
atom_id: CA-R-1548
ref_id: CA-R-1548@24
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Entity/Object/Continuant/Selection
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Requirement)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Method)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Delivery)
  - ANECHOIC_MODEL <+ Atom.Header.Role
  - ANECHOIC_MODEL <+ Package/Implementation
  - ANECHOIC_MODEL <+ Carrier
tier: 1
status: Archived
version: 24
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1548@24-CORE_META_MODEL-DEFINITION--define-specification-content-roles.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/archive
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define Specification Content Roles

## Claim

### Prose Claim


Specification Content Roles (Spec, RMED).


Specification Content Roles (Spec, RMED) **means** the set (Requirement, Method, Evaluation, Delivery) that specifies governed content **and** Entities, including CAPO **and** I.

## Details

- Requirement establishes required outcomes and runtime behavior, including functional and non-functional requirements, and the methodology's own model definitions and constraints.
- Method establishes how those outcomes are achieved, including architecture, coding policies, engineering decisions, construction and authorship conventions.
- Evaluation establishes correctness checks.
- Delivery establishes Carrier contents, representation, **and** placement.

The methodology's own model and specification content are also within this specification domain; RMED is not limited to native Implementation. Subject and Content Role are independent: any RMED Role can govern a Domain, Engineering or global Graph Subject.
