---
atom_family: TKT
atom_id: AN-T-1650
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-26 23:43:42 +0400
---
## Summary

Show dependency-only Subjects

# Summary

Show dependency-only Subjects

## Objective

Add a separate section to each Subject Graph view for Subjects used in subjects.depends_on but never explicitly in subjects.governs within that view's selected Current source set.

## Details

Compare exact canonical Subject values from the two fields. Do not infer Governs membership from ancestors, children or inherited properties. Show each dependency-only Subject once with its referring Atom IDs, in deterministic alphabetical order. Keep the existing primary, properties and instances sections. This section is a derived review aid, not a new Subject root or automatic authority for creating or retiring Atoms.

Update the relevant methodology layout definitions through Drafts first. Integrate the section into the local projection rebuild after the accepted corrections; production tool/runtime code remains outside this Epic. Do not create a separate large mapping report.

## Definition of Done

- Relevant definition Drafts express the accepted section without changing Subject/link meanings.
- The four rebuilt views contain the exact depends_on-minus-governs set for their own sources.
- Referring IDs and alphabetical order match the selected sources; existing sections and source trace remain intact.
