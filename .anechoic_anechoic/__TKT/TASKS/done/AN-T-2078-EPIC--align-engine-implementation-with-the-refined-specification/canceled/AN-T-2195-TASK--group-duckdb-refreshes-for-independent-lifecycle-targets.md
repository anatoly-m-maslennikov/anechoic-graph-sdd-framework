---
atom_family: TKT
atom_id: AN-T-2195
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: task
state:
  status: canceled
  version: 1
  updated_at: '2026-11-12T01:26:29.632971+00:00'
---
## Summary

Group DuckDB refreshes for independent lifecycle targets

## Objective

Reduce the time spent refreshing Workbench during batch Archive and Promote.

## Details

- Review and update the relevant RMEDO before implementation.
- Profile targeted reads, file effects and DuckDB refreshes for a batch of 50.
- Group refreshes for independent targets. Keep the existing order for targets that depend on each other.
- Verify immediate query visibility, per-target outcomes and completed effects when a batch stops on a failure.
- Compare warm timings on the same disposable fixture. The 29.5-second reduced-history baseline was 9.5 seconds for individual Draft creation, 9.4 seconds for batch Archive and 10.5 seconds for batch Promote.