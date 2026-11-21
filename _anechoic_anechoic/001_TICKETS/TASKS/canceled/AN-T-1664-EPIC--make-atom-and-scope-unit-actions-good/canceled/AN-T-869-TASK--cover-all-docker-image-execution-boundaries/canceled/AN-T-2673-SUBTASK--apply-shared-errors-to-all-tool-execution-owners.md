---
atom_family: TKT
atom_id: AN-T-2673
container:
  atom: AN-T-869
priority: 2
context:
  template: task
  label: Subtask
state:
  status: canceled
  version: 4
  updated_at: '2026-11-20T20:06:18.406230+00:00'
---
# Summary

Apply shared errors to all Tool execution owners

## Objective

Wire missing canonical Tool execution boundaries used by direct and Docker/MCP calls. Preserve caller schemas, verified partials, target safety and atomicity; input/artifact failures are WARNING plus explicit output errors. Do not blindly skip an invalid explicit mutation target.

## Details

One Task per file. Each leaf has at most 15 minutes own work; decompose before extending it. Review and update dependants after each predecessor's observed result. Use only broken/related checks, configured Project Temporary State and the selected virtual environment. No production mutation or full-suite run.

### Definition of Done

Focused public Tool checks cover each affected dispatch class and representative previously uncovered adapters; no guessed prefix, silent failure, hidden retry or Journal writes.
