---
atom_family: TKT
atom_id: AN-T-4019
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T19:13:57Z"
---
## Summary

Speed up cold and incremental startup

## Work

Profile cold startup, unchanged restart, and restart after offline
adds, edits, moves, and deletes on the same Project. Reduce repeated
foreground reads and per-directory setup. Fetch and validate only the
foreground checkpoint before readiness. Validate the Archive checkpoint
in the background. Project the declared Summary for the native Atom
index without constructing properties for unrelated headings.
Keep Archive and Realization Graph work in the background.

## Acceptance

Compare time to foreground readiness and peak memory under the same
limits. Report the file scan, Model, Structure, and admission times.
Preserve byte-based change detection, deletion detection, and watcher
coverage. Verify that offline edits use the native delta path when
the schema is compatible.

## Progress

The hash scan reuses a guarded descriptor per carrier directory.
On 5,492 carriers, the median hash scan fell from 2.82 to 2.25 seconds
with matching digests. A Manifest signature under watcher coverage
samples inputs once. Its median fell from 0.38 to 0.21 seconds with
matching signatures. These are host phase measurements.

In the cold host profile, carrier parsing used about 10.5 CPU seconds.
Building source rows and their content properties accounted for about
7 seconds of that total. Native capture now reads the declared Summary
title without building other Content Properties. Median foreground
capture fell from 12.98 to 8.43 seconds on the frozen Project with the
same 5,492 titles, hashes, and ingestion errors.

Kernel scopes checkpoint reads by path before returning them. On the
frozen inventory, the foreground request returns 5,492 of 53,767
paths. The Archive Worker requests the remaining paths after readiness.

Focused checks and all three API startup process tests pass. The
process tests need native macOS FSEvents access, which the shell
sandbox blocks.

On the frozen full-size Project at 1 CPU and 1.5 GiB, first Ready
was 144.07 seconds cold, 33.93 seconds after an unchanged restart,
and 18.89 seconds after offline edits. SQL verified the edit with
unchanged size and mtime, move, deletion, and addition. Both restarts
reused the same database. Cold Archive admission completed at
647.99 seconds. One known conflicting Archive carrier was held out
of the disposable copy. The packaged Model compiler was unchanged.

[Startup profile](file:///Users/am/.bb/thread-storage/thr_5je2jn33zw/startup-profile.yv8b4N/results.json)
