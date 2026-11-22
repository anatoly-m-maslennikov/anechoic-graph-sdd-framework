---
atom_family: TKT
atom_id: AN-T-1669
container:
  component: C45
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-11-07 00:17:17 +0400
---
# Summary

Atoms in new host folders can be missed by the watcher

## Concern

A Draft created inside a newly host-created nested folder did not become query-visible within 90 seconds in the historically reproduced running Workbench runtime. The technical change log recorded directory create/remove observations but no child-file event.

## Evidences

The CA-P-2710 Epic `watcher-latency-review.md` records the probe and its result. CA-E-780 is the linked watcher regression Evaluation.

## Blast radius

Queries can omit Atoms created in new host folders.

## Resolution

Docker bind mounts reported a newly created directory as a file. The watcher now checks the existing path before registering a created or moved directory, registers its watch before publishing the event, and removes registered watches on deletion.

The 5,000-Atom Docker acceptance passed all twelve timed operations, full reread and restart. Mutation-to-query visibility was 1.34–1.40 seconds. Evidence is recorded in the CA-P-2710 acceptance report. This resolves the implementation defect; deployment remains a separate gate.
