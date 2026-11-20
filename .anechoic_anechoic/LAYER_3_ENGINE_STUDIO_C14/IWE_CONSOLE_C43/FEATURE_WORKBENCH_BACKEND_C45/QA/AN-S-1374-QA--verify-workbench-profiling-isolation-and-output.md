---
identity:
  atom_id: AN-S-1374
context:
  container:
    component: C45
  tier: 5
  lens: QA
state:
  status: active
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify Workbench profiling isolation and output

## Claim

### Prose Claim

Run the profiler through the actual DuckDB/DuckPGQ path on a small valid disposable Project. Verify readable cProfile statistics, nonempty allocation diagnostics, dataset/cycle counts, explicit instrumented labels, correct RSS/native-memory labels and identical source hashes before/after. Output remains beneath the selected Project temporary root; bounded cleanup removes the disposable database, or reports its confined retained path without retrying or losing the original failure. Normal performance gates run without cProfile/tracemalloc, and profiler duration never satisfies latency/throughput assertions.
