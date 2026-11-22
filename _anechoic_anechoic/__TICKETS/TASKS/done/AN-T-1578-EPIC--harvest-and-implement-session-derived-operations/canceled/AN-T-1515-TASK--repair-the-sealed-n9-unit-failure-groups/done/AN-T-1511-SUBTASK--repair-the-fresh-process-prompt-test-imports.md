---
atom_family: TKT
atom_id: AN-T-1511
container:
  atom: AN-T-1515
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Repair the fresh process prompt test imports

## Objective

repair three prompt module import frontiers without relaxing the accepted release or source-currentness boundaries.

## Details

- this bounded lane feeds a fresh source-bound N10; retain failed N9 without replay.
- root owns Git, integration, source pins, canonical refresh and actual dispatch. workers preserve other lanes' changes.
- local fixture/source acceptance is not full Release acceptance; installed N remains unchanged.

## Definition of Done

2c16f633a; eleven closure, twenty-one continuation and nine Operator-precheck cases pass.
