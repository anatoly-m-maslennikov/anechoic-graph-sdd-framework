---
identity:
  atom_id: CA-C-756
  ref_id: CA-C-756
context:
  container:
    scope_unit: CA-SU-00
  role: concern
  form: Question
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC
  tier: 3
  concern:
    priority: Medium
state:
  status: active
  version: 1
  updated_at: '2026-11-19T03:33:16.813887+00:00'
destination:
  file:
    name: CA-C-756-QUESTION--decide-whether-bare-migration-relations-may-target-archive-only-atom-lineages.md
    path: .anechoic_anechoic/01_concern
---
## Summary

Decide whether bare migration relations may target archive-only Atom lineages

## Concern

Should a legacy relation with a bare target ID remain in the migration receipt when that ID has only Archived revisions, or should it point to the new stable Atom ID without selecting a revision?

## Details

CA-P-3075 preserves verified relations. Native stable lookup currently resolves Current Atoms. The 67,400-carrier rehearsal found 16,522 unresolved occurrences between rendered sources and identifiable archive-only target lineages. Exact targets are a separate case.

The proposal is to keep the original selectors in the receipt. A rule to retain lineage-level links would also need to define their visibility in the native graph. No historical revision would be selected automatically.

## References

CA-P-3075 and CA-P-3092.