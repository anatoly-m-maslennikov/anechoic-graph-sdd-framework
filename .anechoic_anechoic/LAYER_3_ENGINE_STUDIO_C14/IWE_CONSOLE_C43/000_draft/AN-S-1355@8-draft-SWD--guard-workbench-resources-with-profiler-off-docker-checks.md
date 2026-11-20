---
atom_family: SPEC
atom_id: AN-S-1355
structure:
  container:
    component: C43
  tier: 5
context:
  lens: SWD
state:
  status: draft
  version: 8
  updated_at: '2026-11-14T01:09:22.539314+00:00'
---
## Summary

Guard Workbench resources with profiler-off Docker checks

## Claim

### Prose Claim

Guard Workbench resources with fixed fixture limits, existing speed gates, a
short check, and an opt-in soak in profiler-off Docker.

## Details

- Keep the 1.5-second single-operation, 500-Atom throughput, cold-index, and
  full-reread gates.
- Both checks run without a production endpoint, retry, scheduler, or live
  Project source mutation.

### Controlled fixture

Measure resource regressions in the controlled 5,000-Atom Docker fixture with
allocation and CPU profiling disabled.

- Measure cgroup CPU intervals and current RAM for cold index, warm full reread,
  and a true 15-second idle interval without in-container polling.
- Measure cumulative peak RAM separately.
- Calibrate the fixed limits once for this fixture; never raise a limit
  automatically.

### Controlled-fixture limits

These limits apply only to the fixture with one CPU and a 1,536 MiB RAM cap.

- Cold index and each full reread use at most 25 CPU-seconds and 45
  wall-seconds.
- Current RAM stays at or below 576 MiB; cumulative peak RAM stays at or below
  640 MiB.
- A true 15-second idle uses at most 0.75 CPU-seconds.
- Positive growth over the settled warm baseline stays at or below 64 MiB
  without forced garbage collection.
- No OOM kills, unowned result tables, leaked View pins, leftover removed-source
  cache keys, or undrained work occurs.

Calibrate before acceptance when the fixed workload or runtime boundary changes.
never raise limits to hide a regression. Keep the same process and owner for the
30-minute soak, and reread only after the last leak check.

A fall in current RAM is not growth. Report the full high-to-low spread
separately; allocator or kernel memory release cannot alone fail the growth
check. Current-RAM and cumulative peak ceilings still apply.

### Short check

Keep a short check in the normal Workbench Docker suite. Use the existing
disposable source fixture and Docker ownership boundary.

Check cgroup `oom_kill`, resource values at phase boundaries, and the current
result-table inventory after View reruns and removal.

### Opt-in soak

Keep one identified Workbench owner and process alive for at least 1,800
seconds.

Exercise source creation, update, rename, move, removal and schema changes; run
successful and failed queries; rerun and remove Views; and drain asynchronous
work.

Use fixed quiescent windows without forced garbage collection or a reread/reset.
Persistent growth, orphan result tables, retained View pins, undrained watcher
work, owner replacement, or OOM fails the soak.

Report a stable plateau separately from allocator retention.

Only after final ownership and resource assertions may the soak call
`workbench_reread` through the real Workbench Tool boundary.
