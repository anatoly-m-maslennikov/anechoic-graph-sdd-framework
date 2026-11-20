---
atom_family: TKT
atom_id: AN-T-1853
structure:
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

Review and fix MED duplication with DRY

## Objective

Remove duplicate maintenance while retaining distinct claims and necessary local choices.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [x] Pass one: identify repeated claims, copied inherited policies and duplicated constraints. (ETA: up to 15 min per batch.)
- [x] Fix supported duplicates through shared specification, specialization, merging or replacement as the current model allows. (ETA: up to 15 min per batch.)
- [x] Pass two: recheck the corrected set and its consumers; repair references affected by supported changes. (ETA: up to 15 min per batch.)

## Definition of Done

The reviewed set avoids same-context duplicate maintenance. Shared policies remain reusable, and distinct constraints are not merged merely because they use similar words.
