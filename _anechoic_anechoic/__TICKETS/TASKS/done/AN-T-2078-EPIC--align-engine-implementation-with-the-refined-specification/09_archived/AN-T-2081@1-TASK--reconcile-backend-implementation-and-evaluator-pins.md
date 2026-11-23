---
atom_family: TKT
atom_id: AN-T-2081
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 07:55:38 +0400
---

## Summary

Reconcile Backend implementation and evaluator pins

## Objective

Review I7 and the thin implementation map. Compare each adopted Backend contract against its implementing module and evaluator. Correct only actual mismatches; retain package-time versus runtime schema separation. Do not mass-bump pins or pin called dependencies.

## Subtasks

- [ ] Review and fix the next scoped input batch. (ETA: up to 15 min.)
- [ ] Complete one scoped implementation or verification batch; split before exceeding 20 min.
- [ ] Review and fix the result; record a small P / Work Report. (ETA: up to 15 min.)

## Definition of Done

The stated work has actual source/code/test evidence. Every unresolved or unrun case is explicit; no Task text replaces RMED.
