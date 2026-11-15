---
atom_id: CA-D-397
ref_id: CA-D-397
container:
  scope_unit: CA-SU-13
role: Delivery
form: Decision
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection.Form
  dependencies:
  - CAPRMEDIO_MODEL <+ Entity/Object/Continuant/Term//Artifact
  - CAPRMEDIO_MODEL <+ Atom.Header.Identity.ID
  - CAPRMEDIO_MODEL <+ Carrier
tier: 3
status: Active
version: 26
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-D-397-PROJECT_CONFIGURATION-DECISION--register-caprmedio-type-prefixes.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery/CA-D-397-PROJECT_CONFIGURATION-DECISION--register-caprmedio-type-prefixes.md
  source_atom_id: CA-D-397
  source_atom_revision: 26
  source_sha256: 14c4327017da3bcc55452a5eb0b935fb521415732bc160ffba9f9714c8cb08f2
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register CAPRMEDIO Type prefixes

## Claim

### Prose Claim


fixed lowercase prefixes for listed Artifact Type values.


the following fixed lowercase prefixes **must** be registered **only** for the listed Type values under Artifact; Atom identities use class short names instead.

| Artifact form | Type | Prefix |
|---|---|---|
| `projection` | `catalog` | `catl` |
| `projection` | `map` | `maps` |
| `projection` | `hub` | `hubs` |
| `projection` | `implementation_record` | `irec` |
