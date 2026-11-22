---
atom_family: TKT
atom_id: AN-T-1854
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-11-09 07:59:08 +0400
---

## Summary

Recheck and fix main topics and dependencies

## Objective

Check the Engineering topic branch again after claim-boundary changes.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [x] Pass one: review main topics against each corrected claim, then review dependencies separately. (ETA: up to 15 min per batch.)
- [x] Fix misleading placement, duplicate paths and Scope Unit-shaped topics; check connected literal topic references where a changed address would otherwise become stale. (ETA: up to 15 min per batch.)
- [x] Pass two: query the revised Draft set and fix remaining placement or reference errors. (ETA: up to 15 min per batch.)

## Definition of Done

Main topics and dependencies match the corrected meaning. Topic references remain consistent; unrelated permission rules and non-Engineering semantics are not rewritten.
