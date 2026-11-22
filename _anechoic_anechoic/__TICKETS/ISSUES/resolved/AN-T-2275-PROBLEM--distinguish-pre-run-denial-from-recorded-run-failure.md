---
atom_family: TKT
atom_id: AN-T-2275
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 4
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Distinguish pre-Run denial from recorded Run failure

## Concern

E247's unchanged-Journal denial assertion does not explicitly distinguish a never-started Action Run from an actual started rejected or failed Run.

## Evidences

P1472 found the direct unauthorized-apply case. Shared accepted Run authority requires actual started rejected/failed Runs to retain truthful records. Denial before any Run starts can leave the Journal unchanged; no new Journal owner or extra Workflow is required.

## Blast radius

### Resolution

P1481 saved E247v12 with the pre-Run denial qualification and complete archived v11. P1483 independently accepted the precise delta: unchanged Journal applies only before any Run starts; actual started rejected/failed/parent Runs retain truthful evidence. Source test-contract defect resolved, not implemented runtime proof.

### Original impact

The exact bound repair and independent review precede affected source acceptance. Preserve meaningful source/history and truthful proof; no runtime completion is claimed.
