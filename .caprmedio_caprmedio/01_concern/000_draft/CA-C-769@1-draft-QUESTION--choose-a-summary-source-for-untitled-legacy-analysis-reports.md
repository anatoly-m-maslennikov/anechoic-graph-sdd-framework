---
identity:
  atom_id: CA-C-769
  ref_id: CA-C-769@1-draft
context:
  container:
    scope_unit: CA-SU-00
  role: concern
  form: Question
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO
  tier: 3
  concern:
    priority: Medium
state:
  status: draft
  version: 1
  updated_at: '2026-11-19T14:00:38.187508+00:00'
destination:
  file:
    name: CA-C-769@1-draft-QUESTION--choose-a-summary-source-for-untitled-legacy-analysis-reports.md
    path: .caprmedio_caprmedio/01_concern/000_draft
---
## Summary

Choose a Summary source for untitled legacy Analysis reports

## Concern

May the migration use the original filename words as the Summary
for ten Current reports whose Markdown has no title?

## Details

CA-A-040 through CA-A-049 start with “Task, scope, and boundaries.”
The original FPF reports are recoverable in Git and have the same
first heading. Their filenames distinguish the reports.

Proposed disposition. Use the words of the original report's filename
after removing the timestamp and file extension. Insert a Summary
section in the migrated copy and preserve the whole original body.
Place the reports under TKT Assets.

## References

CA-P-3075, CA-C-755.
