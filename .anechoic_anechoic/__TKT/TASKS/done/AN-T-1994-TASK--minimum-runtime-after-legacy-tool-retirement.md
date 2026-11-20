---
atom_family: TKT
atom_id: AN-T-1994
structure:
  container:
    component: C15
  priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: 2026-11-09 23:57:47 +0400
---

## Summary

Minimum runtime after legacy Tool retirement

## Objective

Retire legacy Tool code and retain Workbench, standalone Subject/Topics builders, host local/public releases, and only the shared dependencies needed by those entry points.

## Definition of Done

Remove unused providers, mutation/query wrappers, selected execution, orchestration and worker paths with their exclusive tests and stale package copy. Preserve retained parsing, isolation, diagnostics, Journal append and release behavior; verify the changed boundaries with focused checks. Record the actual results and remaining gaps in the Work Report. Deployment and source Atom reconciliation are separate work.
