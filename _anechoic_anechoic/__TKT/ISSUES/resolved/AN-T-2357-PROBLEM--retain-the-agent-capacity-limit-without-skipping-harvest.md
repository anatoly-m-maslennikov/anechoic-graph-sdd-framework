---
atom_family: TKT
atom_id: AN-T-2357
structure:
  container:
    component: C00
  priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Retain the Agent capacity limit without skipping harvest

## Concern

The third fresh harvest Agent could not be spawned because the available Agent thread limit was reached.

## Evidences

Two fresh leaf Agents1269/1270 were created successfully. A third request returned agent thread limit reached; live inventory confirms root, completed1200 and two running leaves. Root will execute the independent1271 leaf as its one assigned Agent rather than report a nonexistent third worker or bypass source coverage.

## Blast radius

Dispatch capacity only. No change to Epic scope or completed-source counts; root's1271 task must retain its own firstclock/input/output/frontier and bounded estimate.
