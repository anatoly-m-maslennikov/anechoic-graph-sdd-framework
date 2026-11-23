---
atom_family: TKT
atom_id: AN-T-1509
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 08:47:53 +0400
---
## Summary

Repair the isolated container runtime fixtures

# Summary

Repair the isolated container runtime fixtures

## Objective

repair Runtime.image test initialization and Compose command-boundary fixtures without relaxing the accepted release or source-currentness boundaries.

## Details

- this bounded lane feeds a fresh source-bound N10; retain failed N9 without replay.
- root owns Git, integration, source pins, canonical refresh and actual dispatch. workers preserve other lanes' changes.
- local fixture/source acceptance is not full Release acceptance; installed N remains unchanged.

## Definition of Done

d1be603f6; twenty-two cases pass; actual Docker E2E remains a separate required gate.
