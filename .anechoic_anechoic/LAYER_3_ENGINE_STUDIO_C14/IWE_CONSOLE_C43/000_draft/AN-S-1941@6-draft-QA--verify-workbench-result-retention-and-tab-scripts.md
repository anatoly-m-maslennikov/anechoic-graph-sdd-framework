---
identity:
  atom_id: AN-S-1941
context:
  container:
    component: C43
  tier: 5
  lens: QA
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T00:32:45.296333+00:00'
---
## Summary

Verify Workbench result retention and Tab scripts

## Claim

### Prose Claim

Verify shared Workbench result retention and Tab SQL through real MCP and
browser interfaces.

## Details

- Settings edits alone change neither source files nor the watcher log.

### Startup settings

- A missing settings file gives a TTL of 3,600 seconds.
- A valid TTL of one second takes effect only after restart or reread.
- A TTL of zero fails through stderr. Verify there is no default fallback.
- Verify the runtime settings file is outside the watcher root.

### Shared result cache

- Run through one interface and inspect or page through the other.
  Verify both surfaces agree.
- Record creation time with a monotonic clock.
- Before TTL, an unpinned result is available. After TTL, idle, Run, or Page
  cleanup may expire it.
- An open View pins a result beyond TTL. Closing unpins it.
  A young result stays available and an old one may expire.
- Verify retention needs no heartbeat, lease, crash recovery, scheduler, or service.
- Rerun drops the prior result before replacement. A failed replacement leaves
  the prior ID unavailable.
- Restart clears transient tables and IDs and rebuilds the Projection.
  Saved queries and the View Journal survive.

### Tab SQL

- Unfinished SQL is editable. Run and Check accept one complete query and
  reject multiple statements under CA-R-2728.
- Run & Save stores the exact submitted SQL. Save View stores the full Tab SQL.
