---
atom_family: SPEC
atom_id: AN-S-2254
container:
  component: C45
tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-13T15:55:29.217347+00:00'
---
## Summary

Profile Workbench without changing source files

## Claim

### Prose Claim

An explicitly requested Workbench diagnostic run must report CPU hotspots, Python allocations, process memory and DuckDB-managed memory without changing source files, the live Workbench database or the live MCP process. Profiling is opt-in; ordinary latency, throughput and rebuild acceptance tests run without instrumentation.

The report records runtime/build context, dataset and rebuild-cycle counts, instrumented timings, Python current/peak allocation bytes and top traces, process high-water RSS with byte units, and DuckDB-managed buffer memory. State unavailable measurements explicitly; RSS is not current live memory, and profiled durations are diagnostics rather than performance-acceptance timings.
