---
atom_id: CA-D-339
ref_id: CA-D-339
container:
  scope_unit: CA-SU-13
role: Delivery
form: Decision
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/File
  dependencies:
  - "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization"
  - ANECHOIC_MODEL <+ Event Record
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Journal
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Atom.Header.Context.Role
tier: 3
status: Active
version: 29
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-D-339-PROJECT_CONFIGURATION-DECISION--serialize-the-shared-project-journal.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery/CA-D-339-PROJECT_CONFIGURATION-ENG_DECISION--serialize-the-shared-project-journal.md
  source_atom_id: CA-D-339
  source_atom_revision: 29
  source_sha256: b9a83c8c50c35735c5cc0328576f7db67b5ba3b1d7e20f16c2dd6869353b1279
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Serialize the shared Project Journal

## Claim

### Prose Claim


the shared Project-control Work Journal's serialization.


the shared Project Work Journal **must** materialize its logical event table by serializing its ordered event Records as append-only NDJSON File Carrier segments **in** `.anechoic_<project_name>/_journal/` **or** its registered subdirectories. these segments **must** remain Carriers of the same Journal, **not** separate Journals for Scope Units, Content Roles, workflows, **or** derived log views. describing the Journal as a table does **not** replace this registered serialization **or** require a database Carrier.

## Details

This serialization governs the Project-control Work Journal, not every runtime technical or business Journal. Runtime Journal Delivery may use configured local or remote databases and logging sinks.
