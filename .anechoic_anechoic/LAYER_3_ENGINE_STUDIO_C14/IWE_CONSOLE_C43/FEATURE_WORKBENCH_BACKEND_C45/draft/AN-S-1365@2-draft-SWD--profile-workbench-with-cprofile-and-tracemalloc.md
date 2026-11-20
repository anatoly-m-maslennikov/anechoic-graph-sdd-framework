---
identity:
  atom_id: AN-S-1365
context:
  container:
    component: C45
  tier: 4
  lens: SWD
state:
  status: draft
  version: 2
  updated_at: '2026-11-14T01:09:25.218226+00:00'
---
## Summary

Profile Workbench with cProfile and tracemalloc

## Claim

### Prose Claim

Profile Workbench through an isolated development CLI with confined output,
bounded cleanup, and opt-in instrumentation.

## Details

### CLI and output

Run the diagnostic through an explicit development CLI with the selected Project
root and an optional output directory constrained beneath its configured
temporary root. Write `cpu.pstats` and `report.json` there.

### Isolated execution

Use cProfile and tracemalloc in a separate CLI run over the current reader,
materializer, and QueryStore with an isolated disposable database. Measure
initial indexing and three full rebuild cycles, closing superseded owners.

### Bounded cleanup

Keep disposable databases separate from sources and the live runtime. Attempt
bounded cleanup; if interrupted or denied, report the confined retained path
without retrying or modifying sources.

### Instrumentation boundary

Add no dependency, endpoint, background profiler, or automatic instrumentation.
