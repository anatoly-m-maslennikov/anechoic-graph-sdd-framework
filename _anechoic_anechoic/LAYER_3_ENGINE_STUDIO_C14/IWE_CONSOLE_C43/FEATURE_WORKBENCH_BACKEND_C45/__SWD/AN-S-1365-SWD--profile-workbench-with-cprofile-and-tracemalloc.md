---
atom_family: SPEC
atom_id: AN-S-1365
structure:
  container:
    component: C45
  tier: 4
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Profile Workbench with cProfile and tracemalloc

## Claim

### Prose Claim

Run the diagnostic through an explicit development CLI with the selected Project root and optional output directory constrained beneath its configured temporary root. Write `cpu.pstats` and `report.json` there. Use cProfile and tracemalloc in a separate CLI run over the current reader, materializer and QueryStore with an isolated disposable database; measure initial indexing and three full rebuild cycles, closing superseded owners. Add no dependency, endpoint, background profiler or automatic instrumentation. Keep disposable databases separate from sources/live runtime and attempt bounded cleanup; if cleanup is interrupted or denied, report the confined retained path without retrying or modifying sources.
