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
  version: 7
  updated_at: '2026-11-14T01:09:13.393938+00:00'
---
## Summary

Verify Workbench profiling isolation and output

## Claim

### Prose Claim

Verify profiling output and memory labels, source isolation, bounded cleanup,
and separation from ordinary performance gates.

## Details

- Verify identical source hashes before and after profiling.

### Profiling output

Run the profiler through the actual DuckDB/DuckPGQ path on a small valid
disposable Project.

- Verify readable cProfile statistics and nonempty allocation diagnostics.
- Verify dataset and cycle counts.
- Verify explicit instrumented labels and correct RSS/native-memory labels.

### Confined cleanup

Verify output remains beneath the selected Project temporary root. Bounded
cleanup removes the disposable database or reports its confined retained path
without retrying or losing the original failure.

### Performance gates

Normal performance gates run without cProfile/tracemalloc. Profiler duration
never satisfies latency or throughput assertions.
