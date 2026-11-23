---
atom_family: TKT
atom_id: AN-T-3288
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 23:34:59 +0400
---
## Summary

Update Type-Qualified Status Authority

# Update Type-Qualified Status Authority

**when** CA-P-911 is Done, **then** the Assignee **must** make every governed Status Property resolve from the complete Entity-Type context.

## Scope

`((every CA-P-905 frontier entry assigned to TYPE_QUALIFIED_STATUS) union (every replacement or new authority Atom created from such an entry))`

## Definition of Done

the Task is **not done if** (one global Atom Status value domain overrides Type-qualified Status domains **or** Requirement Status does not resolve as `Atom/Content Role: Requirement/Status` **or** Method, Evaluation, or Delivery Status does not resolve under its own Content Role-qualified path **or** Task Status does not resolve as `Atom/Content Role: Plan/Type: Task/Status` **or** any RMED Status lacks the Core values (Draft, Active, Archived) **or** Task Status lacks the Core values (Draft, Active, Done, Canceled) **or** Requirement and Task Status cannot have different allowed values **or** more than one current Status is assigned to one governed Artifact **or** prior Status transitions are required to coexist in current metadata instead of the Journal **or** any replaced conflicting authority remains active).

## Details

keep allowed Status values open to each qualified Entity Type. do not introduce a second revision-disposition axis. leave the shared Carrier key and status-folder materialization to CA-P-913.
