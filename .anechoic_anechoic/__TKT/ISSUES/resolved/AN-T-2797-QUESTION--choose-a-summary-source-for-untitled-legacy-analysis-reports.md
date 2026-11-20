---
identity:
  atom_id: AN-T-2797
context:
  container:
    component: C00
  tier: 3
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-19T14:00:38.187508+00:00'
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

The Operator approved the original report's filename as the Summary
source for these ten Current reports. Remove the timestamp and file
extension from the filename words. Insert a Summary in the migrated copy,
preserve the whole original body, and place the report under TKT Assets.

## References

CA-P-3075, CA-C-755.
