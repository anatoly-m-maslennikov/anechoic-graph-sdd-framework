---
atom_family: TKT
atom_id: AN-T-1529
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 20:02:00 +0400
---
## Summary

Repair N12 selected Run fixtures

# Summary

Repair N12 selected Run fixtures

## Objective

repair confirmed selected-run/MCP fixture or code mismatches while preserving existing authority, source freshness and recording contracts.

## Details

- this lane owns 4 failing cases from the frozen N12 Unit report, not a new scope expansion.
- use disposable fixtures; preserve actual Run, runtime, Journal and source snapshot evidence.
- coordinate shared production dependencies instead of overlapping another worker. root integrates accepted changes and current pins.

## Definition of Done

the observed failures are explained and fixed against current authority; focused regression suites pass and independent review accepts the bounded change. actual full Release acceptance remains with the parent Plan.

## Result

the selected-execution suite passes 20 tests and the isolated MCP suite passes 4 tests. the fixtures copy exact bound sources into disposable Projects, allow bounded gateway cold start and correctly stop before a next Step while terminal recording is pending. independent review accepts the changes; actual all-route release proof remains separate.
