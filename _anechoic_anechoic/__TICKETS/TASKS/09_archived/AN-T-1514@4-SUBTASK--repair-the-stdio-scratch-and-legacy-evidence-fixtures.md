---
atom_family: TKT
atom_id: AN-T-1514
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 08:16:43 +0400
---
## Summary

Repair the stdio scratch and legacy evidence fixtures

# Summary

Repair the stdio scratch and legacy evidence fixtures

## Objective

repair runner TMPDIR fixtures and explicit historical Actor bytes without relaxing the accepted release or source-currentness boundaries.

## Details

- this bounded lane feeds a fresh source-bound N10; retain failed N9 without replay.
- root owns Git, integration, source pins, canonical refresh and actual dispatch. workers preserve other lanes' changes.
- local fixture/source acceptance is not full Release acceptance; installed N remains unchanged.

## Definition of Done

7aee87a46; four MCP and eighteen declared-Subject cases pass; no production changes.
