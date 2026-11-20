---
identity:
  atom_id: AN-T-2920
context:
  container:
    atom: AN-T-2791
  template: task
state:
  status: "done"
  version: 2
  updated_at: "2026-11-20T12:33:01.872182+00:00"
---
## Summary

Integrate and verify Manifest Runtime

## Work

Wire the compiler and hosts into native startup and Local Release. Verify reload, failed rebuild recovery, consistent snapshots for in-flight operations, and restart on Model changes. Verify Structure-only changes keep the database and consumers running.

## Verification

Isolated Local Release ran 329 test modules and 2,590 tests, with five
skips and no failed modules. The installed candidate started with the
compiled Model and separate Host processes. Local Release retained Docker
images whose ownership it could not verify.

A valid Structure edit published a new snapshot. An invalid edit held the
last valid snapshot. Both Hosts, the MCP consumer, and a cached Workbench
query survived reload. The operation test verified one pinned snapshot per
lifecycle write. The Model restart test loaded a new generation only after
restart.

Evidence: `.anechoic_tmp/ca-p-3075/manifest-runtime-work/`.
