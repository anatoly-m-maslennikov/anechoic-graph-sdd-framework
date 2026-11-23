---
atom_family: TKT
atom_id: AN-T-1656
container:
  atom: AN-T-2488
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:51:59 +0400
---

## Summary

Implement source-backed SQL updates

## Objective

Implement the adopted source-mutation contracts and their lifecycle dependencies from R2728, M462, E674 and O240. Do not mutate Projection facts as source authority or restore retired Tool routes.

## Subtasks

- [ ] Review and fix the next bounded input batch. (ETA: up to 15 min.)
- [ ] Implement or verify one scoped batch; split before 20 min.
- [ ] Independently review, fix and record actual results. (ETA: up to 15 min.)

## Definition of Done

Actual implementation and acceptance evidence covers the admitted batch; record unresolved and unrun cases. Tasks do not replace RMEDO.
