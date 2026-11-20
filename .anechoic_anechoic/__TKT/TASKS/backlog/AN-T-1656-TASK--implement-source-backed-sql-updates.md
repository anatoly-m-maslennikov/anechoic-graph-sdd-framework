---
identity:
  atom_id: AN-T-1656
context:
  container:
    atom: AN-T-2488
  tier: 4
  template: task
state:
  status: backlog
  version: 2
  updated_at: 2026-11-11 01:59:27 +0400
---

## Summary

Implement source-backed SQL updates

## Objective

After P2913 adopts the proposal set, implement the admitted source-mutation contracts and their lifecycle dependencies. The proposal inputs include R2728, M550, E822 and O242; refresh their Current identities before dispatch. Do not mutate Projection facts as source authority or restore retired Tool routes.

## Subtasks

- [ ] Review and fix the next bounded input batch. (ETA: up to 15 min.)
- [ ] Implement or verify one scoped batch; split before 20 min.
- [ ] Independently review, fix and record actual results. (ETA: up to 15 min.)

## Definition of Done

Actual implementation and acceptance evidence covers the admitted batch; record unresolved and unrun cases. Tasks do not replace RMEDO.
