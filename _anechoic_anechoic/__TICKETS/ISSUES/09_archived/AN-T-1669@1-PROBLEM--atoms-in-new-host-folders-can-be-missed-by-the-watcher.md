---
atom_family: TKT
atom_id: AN-T-1669
container:
  component: C45
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-11-06 20:37:19 +0400
---
## Summary

Atoms in new host folders can be missed by the watcher

# Summary

Atoms in new host folders can be missed by the watcher

## Concern

A Draft created inside a newly host-created nested folder did not become query-visible within 90 seconds in the historically reproduced running Workbench runtime. The technical change log recorded directory create/remove observations but no child-file event.

## Evidences

The CA-P-2710 Epic `watcher-latency-review.md` records the probe and its result. CA-E-780 is the linked watcher regression Evaluation.

## Blast radius

Queries can omit Atoms created in new host folders.
