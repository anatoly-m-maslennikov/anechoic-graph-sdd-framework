---
atom_family: SPEC
atom_id: AN-S-1892
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 21
  updated_at: 2026-10-25 00:56:39 +0400
---
## Summary

Register Project Current-Scope Content Role Directories

# Summary

Register Project Current-Scope Content Role Directories

## Scope

administrative Content Role directory placement at the ANECHOIC Project root **and** **in** **every** descendant Scope Unit, including `CORE_META_MODEL`, `INSTALLED_EXTENSIONS`, **and** `PROJECT_CONFIGURATION`.

## Claim

**every** Scope Unit **in** the ANECHOIC Project **must** use the same administrative Content Role directory mapping directly under its own authority directory for current-scope placement:

- Concern: `01_concern/`;
- Analysis: `02_analysis/`;
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
