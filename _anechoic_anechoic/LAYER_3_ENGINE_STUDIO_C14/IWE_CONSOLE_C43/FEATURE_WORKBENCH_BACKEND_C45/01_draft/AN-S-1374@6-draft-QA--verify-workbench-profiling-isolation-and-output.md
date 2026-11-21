---
atom_family: SPEC
atom_id: AN-S-1374
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 6
  updated_at: '2026-11-13T20:47:48.790558+00:00'
---
## Summary

Verify Workbench profiling isolation and output

## Claim

### Prose Claim

Run the profiler through the actual DuckDB/DuckPGQ path on a small valid disposable Project. Verify readable cProfile statistics, nonempty allocation diagnostics, dataset and cycle counts, explicit instrumented labels, correct RSS and native-memory labels, and identical source hashes before and after the run.

Verify that output stays beneath the selected Project temporary root. Bounded cleanup removes the disposable database or reports its confined retained path without retrying or losing the original failure.

Run normal performance gates without cProfile or tracemalloc. Profiler duration must not satisfy latency or throughput assertions.
