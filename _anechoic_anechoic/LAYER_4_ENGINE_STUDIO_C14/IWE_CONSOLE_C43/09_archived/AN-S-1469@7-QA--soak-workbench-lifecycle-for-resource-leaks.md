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
  version: 7
  updated_at: '2026-11-14T01:09:19.338972+00:00'
---
## Summary

Soak Workbench lifecycle for resource leaks

## Claim

### Prose Claim

Verify continuous ownership, workload progress, resource measurements, resource
stability, exact inventories, View retention, and post-soak reread.

## Details

### Continuous ownership

When explicitly enabled, run one identified real Workbench watchdog, DuckDB
owner, and service continuously for at least 1,800 seconds against an owned
disposable Project.

Do not restart, reread, or replace the owner before final leak assertions.

### Workload progress

- Repeatedly create, update, rename, move, and remove sources with valid unique
  numeric IDs.
- Edit model Declarations and verify their data refreshes while compiled columns
  stay fixed.
- Run successful and failed queries, rerun and remove Views, and wait for
  asynchronous work to drain.

Verify source changes become visible and errors do not stop later work. Verify
queues drain. Drain query-log writes with a completed FIFO barrier; a queue-size
sample alone is not proof of completion.

### Phase measurements

Before and after warm-up, workload, and fixed quiescent phases, record cgroup
CPU interval deltas, current and cumulative peak RAM, owner PID and identity,
and exact result-table, result-pin, and watcher-work inventories.

Do not force garbage collection.

### Resource stability

Verify no OOM occurs and the same owner remains present. Report a stable memory
plateau separately from allocator retention; a sustained growth trend fails the
soak.

### Exact inventories

Verify final inventories return to their expected baseline. Use exact SQL table
oracles for result tables and pins; compare SQL table names with the store owner
map and pins with open View results.

Check reader, reference, and every relation-state map against expected final
inventory, including absence of empty outgoing relation entries for removed
unique source IDs.

### View lifecycle

Verify each View rerun drops its prior result, closed Views unpin their results,
and TTL cleanup removes expired unpinned results.

Keep an anchor View open beyond the short fixture TTL and verify its owned
result table remains available. Closing that View releases its pin; only after
TTL cleanup must its table disappear.

### Reread reset

After final leak assertions, call `workbench_reread` through the real Workbench
Tool boundary and verify the expected reset separately.

### Test boundaries

The soak is opt-in and must not make the ordinary test suite wait 30 minutes. It
uses no profiler, new production endpoint, or live Project mutation.
