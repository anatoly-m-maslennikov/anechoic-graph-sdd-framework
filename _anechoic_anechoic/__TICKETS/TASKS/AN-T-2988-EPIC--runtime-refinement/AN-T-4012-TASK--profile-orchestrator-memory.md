---
atom_family: TKT
atom_id: AN-T-4012
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T18:36:29Z"
---
## Summary

Profile Orchestrator memory

## Work

Profile a disposable runtime on the same Project snapshot. Record
Orchestrator memory at process start, watcher baseline, Worker request
and reply, Kernel admission, Archive start, Graph start, and idle.
Attribute Python heap allocations and account for the difference
between heap size and process memory. Compare matched old and current
builds if the old image is available.

## Acceptance

Identify the largest live allocations and report peak and retained
memory by phase and process. Account for the reported 410 MiB sample as
far as the reproduced workload permits. Keep the separate 59 MiB
Archive scan measurement distinct. Report evidence before changing
memory behavior.

## Evidence

On the same frozen 55,493-file Project, Orchestrator reached 463 MiB
in the current image and 486 MiB in the preceding image around
foreground admission. Both fell below 183 MiB after the peak. The
heap trace tied the growth to retained watcher snapshots. The two
scan callbacks keep their own snapshot alive until cyclic collection.

The isolated 11-scan check peaked at 115 MiB with the original
callbacks and 28 MiB after breaking the references. AN-T-4016 tracks
the fix. The current full-size Archive load requested native
reconciliation, so that run did not reach stable idle.

[Profile and raw evidence](file:///Users/am/.bb/thread-storage/thr_5je2jn33zw/orchestrator-memory.Td8GE7/report.md)
