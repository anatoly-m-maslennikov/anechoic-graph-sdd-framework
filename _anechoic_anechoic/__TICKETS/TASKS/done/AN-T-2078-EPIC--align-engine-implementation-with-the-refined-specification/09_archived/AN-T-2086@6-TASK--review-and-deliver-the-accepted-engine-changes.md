---
atom_family: TKT
atom_id: AN-T-2086
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 6
  updated_at: 2026-11-11 00:29:06 +0400
---

## Summary

Review and deliver the accepted Engine changes

## Objective

Review the combined implementation against adopted RMED, fix confirmed issues, then perform the authorized local delivery with its actual checks. Record Current spec versions, tests, deployment and remaining deferrals separately.

## Subtasks

- [ ] Review and fix the next scoped input batch. (ETA: up to 15 min.)
- [ ] Complete one scoped implementation or verification batch; split before exceeding 20 min.
- [ ] Review and fix the result; record a small P / Work Report. (ETA: up to 15 min.)

## Definition of Done

The stated work has actual source/code/test evidence. Every unresolved or unrun case is explicit; no Task text replaces RMED.

## Release-test cleanup check

- [ ] Recheck C567 against the retained release test runner and current Docker fixtures. The historical failing selected-Workflow fixture is no longer present.
- [ ] Reproduce any applicable interrupted-run or failed-start cleanup defect, then prepare the smallest confirmed repair and regression coverage. Split investigation, repair and verification into batches of at most 15–20 minutes.
- [ ] Record exact resource ownership and outcomes under the existing cleanup policies. Do not restore retired Workflow tests or treat historical evidence as proof of a current failure.
