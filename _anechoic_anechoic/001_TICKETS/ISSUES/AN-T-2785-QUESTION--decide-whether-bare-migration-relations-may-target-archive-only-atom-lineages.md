---
atom_family: TKT
atom_id: AN-T-2785
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-19T03:33:16.813887+00:00'
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