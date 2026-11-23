---
atom_family: TKT
atom_id: AN-T-2088
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 19:08:55 +0400
---

## Summary

Add the query-inaccessible Atom audit table

## Objective

Create and review RMED for a table listing every Atom whose content is not accessible through query_run. Then implement and test it against readable and unreadable source cases.

## Subtasks

- [ ] Create or update the related RMED; review and fix it. (ETA: up to 20 min per batch.)
- [ ] Gather applicable Method Policies and implement the accepted RMED. (ETA: up to 20 min per batch.)
- [ ] Add E2E coverage, review and fix the result, and record a small Work Report. (ETA: up to 20 min per batch.)

## Definition of Done

The accepted RMED defines the table and its checks. Query-visible results identify the actual affected sources; E2E evidence covers both positive and negative cases. This Task does not replace the specification or authorize automatic source repair.
