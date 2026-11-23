---
atom_family: SPEC
atom_id: AN-S-2254
container:
  component: C45
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Profile Workbench without changing source files

## Claim

### Prose Claim

An explicitly requested Workbench diagnostic run must report CPU hotspots, Python allocations, process memory and DuckDB-managed memory without changing source files, the live Workbench database or the live MCP process. Profiling is opt-in; ordinary latency, throughput and rebuild acceptance tests run without instrumentation.
