---
atom_family: TKT
atom_id: AN-T-4023
container:
  atom: AN-T-4019
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 1
  updated_at: "2026-11-26T20:13:24Z"
---

## Summary

Measure startup at two CPUs

## Work and acceptance

Repeat the cold, unchanged, and offline-edit startup runs with two
CPUs. Retain the one-CPU profile's image, source, scheduling, and
1.5 GiB memory limit.

Compare first Ready, Archive completion, and peak memory. Confirm
that the two restarts reuse the database and preserve the offline
edits in SQL. Keep the Graph scheduling change out of the comparison.

## Verification

First Ready at one and two CPUs, respectively, was 144.07 and 85.07
seconds cold, 33.93 and 14.05 seconds unchanged, and 18.89 and 12.76
seconds after offline edits. Cold Archive completed in 647.99 and
279.18 seconds. Both cold runs reached 1.5 GiB with no OOM kill.

The two restarts reused the database and matched the one-CPU SQL
results. The CPU comparison used the original Graph schedule and
one run per case.

[CPU comparison](file:///Users/am/.bb/thread-storage/thr_5je2jn33zw/startup-profile-2cpu.I7HQxv/cpu-comparison.json)
