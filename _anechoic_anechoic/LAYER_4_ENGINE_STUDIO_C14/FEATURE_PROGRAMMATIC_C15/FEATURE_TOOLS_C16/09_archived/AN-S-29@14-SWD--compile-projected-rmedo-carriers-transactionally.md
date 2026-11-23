---
atom_family: SPEC
atom_id: AN-S-29
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Compile Projected RMEDO Carriers Transactionally

# Compile Projected RMEDO Carriers Transactionally

**to** compile Applicable Methodology, `COMPILE_APPLICABLE_METHODOLOGY` **must** implement CA-M-224 mechanically, stage the complete projected RMEDO Carrier set under `.anechoic_runtime`, preserve **and** revalidate **every** selected Source Carrier's repository-relative path, Atom ID, Revision, byte digest, and source Relation, **and** replace **only** files **in** `04_requirement`, `05_method`, `06_evaluation`, `07_delivery`, **and** `09_operations` through atomic file replacement with complete transaction rollback on failure. A deleted derived role tree must be fully regenerated from the same current resolved frontier; the transaction never edits source authority.

## Sources

- CA-R-1842 v1; CA-M-224; CA-O-157 v2.
