---
atom_family: TKT
atom_id: AN-T-1528
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 08:16:43 +0400
---
## Summary

Repair N12 sealed suite fixtures

# Summary

Repair N12 sealed suite fixtures

## Objective

repair source-sealed graph-state and suite fixtures without adding Git metadata to runtime packages or weakening repository/currentness checks.

## Details

- this lane owns 2 failing cases from the frozen N12 Unit report, not a new scope expansion.
- use disposable fixtures; preserve actual Run, runtime, Journal and source snapshot evidence.
- coordinate shared production dependencies instead of overlapping another worker. root integrates accepted changes and current pins.

## Definition of Done

the observed failures are explained and fixed against current authority; focused regression suites pass and independent review accepts the bounded change. actual full Release acceptance remains with the parent Plan.

## Result

the sealed graph fixture passes 14 tests without synthetic Git metadata; the specific sealed-workspace mutation test passes in 58.093 seconds and asserts that no .git exists. independent review accepts both test-only changes. no whole-suite or actual release pass is inferred.
