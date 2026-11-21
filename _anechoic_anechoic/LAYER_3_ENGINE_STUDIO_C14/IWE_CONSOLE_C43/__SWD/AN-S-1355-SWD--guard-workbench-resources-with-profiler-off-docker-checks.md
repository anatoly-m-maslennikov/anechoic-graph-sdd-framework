---
atom_family: SPEC
atom_id: AN-S-1355
container:
  component: C43
tier: 5
context:
  lens: SWD
state:
  status: active
  version: 7
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Guard Workbench resources with profiler-off Docker checks

## Claim

### Prose Claim

Measure Workbench resource regressions in the controlled 5,000-Atom Docker fixture with allocation and CPU profiling disabled: cgroup CPU intervals and current RAM for cold index, warm full reread and a true 15-second idle interval without in-container polling, plus cumulative peak RAM. Calibrate the fixed limits below once for that fixture; never raise one automatically. Preserve the existing 1.5-second single-operation, 500-Atom throughput, cold-index and full-reread gates.

Keep a short check in the normal Workbench Docker suite and an opt-in 30-minute leak soak. Neither adds a production endpoint, profiler, retry, scheduler or live Project source mutation.

## Details

The short check uses the existing disposable source fixture and Docker ownership boundary. It checks cgroup `oom_kill`, resource values at phase boundaries, and the current result-table inventory after View reruns and removal.

The opt-in soak keeps one identified Workbench owner and process alive for at least 1,800 seconds while it creates, updates, renames, moves and removes fixture sources and changes schema, runs successful and failed queries, reruns/removes Views, and drains asynchronous work. It uses fixed quiescent windows without forced garbage collection or a reread/reset. Persistent growth, orphan result tables, retained View pins, undrained watcher work, owner replacement or OOM fails it; report a stable plateau separately from allocator retention. Only after final ownership/resource assertions may it call `workbench_reread` through the real Workbench Tool boundary.

## Controlled-fixture limits

The selected 5,000-Atom fixture runs in a disposable Docker container capped at one CPU and 1,536 MiB RAM. Its fixed regression limits are:

- Cold index and each complete reread: at most 25 CPU-seconds and 45 wall-seconds.
- Current cgroup RAM: at most 576 MiB.
- Cumulative cgroup peak RAM: at most 640 MiB.
- True 15-second idle interval: at most 0.75 CPU-seconds.
- Positive current-RAM growth above the settled warm baseline: at most 64 MiB, without forced garbage collection.
- No OOM kills, unowned result tables, leaked View pins, leftover removed-source cache keys or undrained work.

These are regression limits for this recorded fixture and runtime cap, not universal Project limits. Calibrate before acceptance when the fixed workload or runtime boundary changes; never raise limits to turn a regression green. The 30-minute phase keeps the same process and owner throughout. Full reread follows its final leak check.

A fall in current RAM is not growth. Report the full high-to-low spread separately; it cannot fail the growth check merely because the allocator or kernel released memory. The current-RAM and cumulative peak ceilings still apply.
