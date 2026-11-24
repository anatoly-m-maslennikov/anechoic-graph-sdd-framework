---
atom_family: SPEC
atom_id: AN-S-1941
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: '2026-11-12T12:34:26.377451+00:00'
---
## Summary

Verify Workbench result retention and Tab scripts

## Claim scope

The shared Workbench result cache, open-View pinning, runtime TTL setting and whole-query execution as observed through MCP and the web frontend.

## Claim

### Prose Claim

Through real MCP/browser surfaces of one shared backend, verify start-time `.anechoic_runtime/anechoic_runtime_settings.toml`: missing is 3,600 seconds; positive `result_ttl_seconds=1` takes effect only after explicit restart/reread; edit alone does not hot reload; invalid `0` fails stderr boundary, never defaults; settings lie outside watcher root and create no change-log event.

Run through one surface and page/inspect through the other to prove one owner/cache. Record monotonic creation: unpinned result is available before TTL and may expire after it through existing idle/Run/Page cleanup. Open View pins beyond TTL; closing unpins while young survives/old may expire—no heartbeat/lease/crash recovery/scheduler/service. Rerun drops old result before replacement; failed replacement does not restore old ID. Restart removes transient tables/IDs while rebuilding Projection and retains saved query/View Journal.

Keep unfinished text editable. Run and Check accept one complete query and reject multiple statements under CA-R-2728. Verify Run & Save stores the exact submitted SQL and Save View stores the complete SQL text. Pass only if real MCP/browser behavior agrees and settings changes alone change neither sources nor watcher log.
