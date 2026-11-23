---
atom_family: SPEC
atom_id: AN-S-4255
container:
  component: C45
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Deliver Workbench profiles under project temporary storage

## Claim

### Prose Claim

Provide an explicit development CLI with the selected Project root and an optional output directory constrained beneath that Project’s configured temporary root. Write cpu.pstats and report.json there. The report includes runtime/build context, dataset and rebuild-cycle counts, instrumented timings, Python current/peak allocation bytes and top allocation traces, process high-water RSS with byte units, and DuckDB-managed memory. State unavailable measurements explicitly; do not present cumulative RSS as current live memory. Keep disposable databases separate from source files and the live runtime database, and attempt bounded cleanup on completion or failure. If cleanup is interrupted or denied, report the retained path under the Project temporary root; do not retry or modify source files.
