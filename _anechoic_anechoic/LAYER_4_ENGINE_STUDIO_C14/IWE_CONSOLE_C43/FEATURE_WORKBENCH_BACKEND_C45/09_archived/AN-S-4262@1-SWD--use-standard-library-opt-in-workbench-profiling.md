---
atom_family: SPEC
atom_id: AN-S-4262
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-07 03:26:51 +0400
---

## Summary

Use standard-library opt-in Workbench profiling

## Claim

### Prose Claim

Use cProfile for CPU calls and tracemalloc for Python allocations in a separate diagnostic CLI run. Reuse the current Workbench reader, materializer and QueryStore with an isolated disposable database. Measure the initial index and three full rebuild cycles; close superseded database owners. Report tracemalloc current/peak Python allocation bytes, process high-water RSS bytes and DuckDB-managed buffer bytes separately. Mark unavailable native measurements unavailable; process high-water RSS is not current live memory. Label all profiled durations as instrumented diagnostics, not performance acceptance timings. Add no dependency, background profiler, runtime endpoint or automatic instrumentation.
