---
atom_family: SPEC
atom_id: AN-S-1469
container:
  component: C43
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Soak Workbench lifecycle for resource leaks

## Claim

### Prose Claim

When explicitly enabled, run one identified real Workbench watchdog, DuckDB owner and service continuously for at least 1,800 seconds against an owned disposable Project. Repeatedly create, update, rename, move and remove sources with valid unique numeric IDs; change declared columns; run successful and failed queries; rerun and remove Views; and wait for asynchronous work to drain. Do not restart, reread or replace the owner before the final leak assertions.

Before and after warm-up, workload and fixed quiescent phases, record cgroup CPU interval deltas, current and cumulative peak RAM, the owner PID and identity, and exact Workbench result-table, result-pin and watcher-work inventories. Do not force garbage collection. The soak passes only when source changes become visible, errors do not stop later work, each View rerun drops its prior result, closed Views unpin their results, TTL cleanup removes expired unpinned results, queues drain, no OOM occurs, the same owner remains present, and final inventories return to their expected baseline. Use exact SQL table oracles for result tables and pins. Report a stable memory plateau separately from allocator retention; report a sustained growth trend as a failure.

## Details

After those assertions, call `workbench_reread` through the real Workbench Tool boundary and verify the expected reset separately. The soak is opt-in and must not make the ordinary test suite wait 30 minutes. It uses no profiler, no new production endpoint and no live Project mutation.

Check reader, reference and every relation-state map against their expected final inventory, including absence of empty outgoing relation entries for removed unique source IDs. Drain query-log writes with a completed FIFO barrier; do not treat a queue-size sample alone as proof of completion. Compare SQL result-table names with the store owner map and compare pins with open View results.

Keep an anchor View open beyond the short fixture TTL and verify that its owned result table remains available. Closing that View releases its pin; only after TTL cleanup must its table disappear.
