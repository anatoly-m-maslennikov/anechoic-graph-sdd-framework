---
atom_id: CA-D-327
ref_id: CA-D-327
container:
  scope_unit: CA-SU-13
role: Delivery
form: Decision
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/Directory
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Delivery)
tier: 3
status: Active
version: 23
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-D-327-PROJECT_CONFIGURATION-DECISION--use-the-project-root-only-for-delivery-carriers.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
---
## Summary

Use the Project Root Only for Delivery Carriers

## Claim

### Prose Claim


Delivery Directory Carriers at the ANECHOIC Project root.


the ANECHOIC Project root **must** carry **only** Delivery Directory Carriers produced for Project Scope Units whose authority Carriers live under `.anechoic_anechoic/` **or** another registered Project-owned Carrier root.
