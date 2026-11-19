---
atom_id: CA-D-324
ref_id: CA-D-324@29
container:
  scope_unit: CA-SU-13
role: Delivery
form: Decision
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier
  dependencies:
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Atom.Header.Role
  - ANECHOIC_MODEL <+ Carrier
  - ANECHOIC_MODEL <+ Carrier/Directory
tier: 3
status: Archived
version: 29
updated_at: 2026-11-02 15:49:28 +0400
carrier_destination:
  file:
    name: CA-D-324@29-PROJECT_CONFIGURATION-ENG_DECISION--register-project-current-scope-content-role-directories.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/07_delivery/archive
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
---
## Summary

Register Project Current-Scope Content Role Directories

## Claim

### Prose Claim


administrative Content Role directory placement at the ANECHOIC Project root **and** **in** **every** descendant Scope Unit, including `CORE_META_MODEL`, `INSTALLED_EXTENSIONS`, **and** `PROJECT_CONFIGURATION`.


**every** Scope Unit **in** the ANECHOIC Project **must** use the same administrative Content Role directory mapping directly under its own authority directory for current-scope placement:

- Concern: `01_concern/`;
- Analysis & Advisory: `02_analysis/`;
- Plan: `03_plan/`;
- Requirement: `04_requirement/`;
- Method: `05_method/`;
- Evaluation: `06_evaluation/`;
- Delivery: `07_delivery/`;
- Implementation: `08_implementation/`;
- Operations: `09_operations/`.

materialize these directories under `CA-D-296-CORE_META_MODEL-DELIVERY--materialize-content-role-directories-on-first-artifact`. preserve specific Carrier placement rules **and** apply Status placement under `CA-D-466-CORE_META_MODEL-DELIVERY--place-carriers-by-applicable-status-delivery`.

## Details

the Project Scope Unit uses `.anechoic_anechoic/` as its authority directory. **every** descendant uses its own declared authority directory **and** reuses this mapping rather than independently defining it.

these administrative directories provide placement; they do **not** become Structural Entities **or** Directory Carriers under `CA-D-451-CORE_META_MODEL-DELIVERY--classify-folders-by-their-carrier-responsibility`.
