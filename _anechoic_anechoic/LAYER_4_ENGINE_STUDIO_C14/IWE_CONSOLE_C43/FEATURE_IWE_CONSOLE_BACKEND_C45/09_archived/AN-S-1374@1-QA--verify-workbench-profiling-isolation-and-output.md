---
atom_family: SPEC
atom_id: AN-S-1374
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-07 03:26:52 +0400
---

## Summary

Verify Workbench profiling isolation and output

## Claim

### Prose Claim

Run the profiler against a small valid disposable Project using the actual DuckDB/DuckPGQ path. Verify readable cProfile statistics, nonempty allocation diagnostics, dataset/cycle counts, explicit instrumented labels, correctly labelled RSS/native memory fields, and identical source-file hashes before and after. Verify output stays within the selected Project temporary root and the disposable database is removed when bounded cleanup succeeds. If cleanup fails, report the confined retained path explicitly; do not retry or lose the original failure. The normal performance gates must run without cProfile or tracemalloc enabled; profiler durations never satisfy their latency or throughput assertions.
