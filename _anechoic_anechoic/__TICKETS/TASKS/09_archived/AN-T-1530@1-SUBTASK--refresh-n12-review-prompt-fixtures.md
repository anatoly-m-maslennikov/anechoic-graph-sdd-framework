---
atom_family: TKT
atom_id: AN-T-1530
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 1
  updated_at: 2026-10-06 18:24:00 +0000
---
## Summary

Refresh N12 review prompt fixtures

# Summary

Refresh N12 review prompt fixtures

## Objective

refresh the exact prompt settings pin and correct the sealed authority fixture, retaining all substantive authorization and no-forcing checks.

## Details

- this lane owns 2 failing cases from the frozen N12 Unit report, not a new scope expansion.
- use disposable fixtures; preserve actual Run, runtime, Journal and source snapshot evidence.
- coordinate shared production dependencies instead of overlapping another worker. root integrates accepted changes and current pins.

## Definition of Done

the observed failures are explained and fixed against current authority; focused regression suites pass and independent review accepts the bounded change. actual full Release acceptance remains with the parent Plan.

## Result

the capability-authority suite passes 6 tests and the RMED prompt contracts pass 17 tests. the exact current default-settings SHA is bound by the prompt manifest and D580 v5, without an unavailable legacy Project-file assertion. independent review preserves substantive Operator authorization and no-forcing checks.
