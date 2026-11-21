---
atom_family: TKT
atom_id: AN-T-1655
container:
  atom: AN-T-2488
priority: 2
context:
  template: task
state:
  status: backlog
  version: 2
  updated_at: 2026-11-11 01:59:27 +0400
---

## Summary

Implement sequential SQL scripts

## Objective

After P2913 adopts the proposal set, implement the admitted script execution and per-statement result contracts. The proposal inputs include R2728, R2729, M550, D673 and O242; refresh their Current identities before dispatch. Verify the accepted read-after-write and failure boundaries through their Evaluations.

## Subtasks

- [ ] Review and fix the next bounded input batch. (ETA: up to 15 min.)
- [ ] Implement or verify one scoped batch; split before 20 min.
- [ ] Independently review, fix and record actual results. (ETA: up to 15 min.)

## Definition of Done

Actual implementation and acceptance evidence covers the admitted batch; record unresolved and unrun cases. Tasks do not replace RMEDO.
