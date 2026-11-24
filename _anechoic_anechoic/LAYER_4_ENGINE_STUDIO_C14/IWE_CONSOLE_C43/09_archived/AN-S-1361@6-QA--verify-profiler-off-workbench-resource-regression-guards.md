---
atom_family: SPEC
atom_id: AN-S-1361
container:
  component: C43
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 6
  updated_at: '2026-11-14T01:09:16.497563+00:00'
---
## Summary

Verify profiler-off Workbench resource regression guards

## Claim

### Prose Claim

Verify resource limits, performance gates, measurement reporting, and View
result retention in the short profiler-off Workbench Docker test.

## Details

### Resource limits

Run the existing disposable 5,000-Atom Workbench Docker fixture with
`tracemalloc` and CPU profiling disabled.

Take cgroup snapshots immediately before and after cold index, warm full reread,
and a true 15-second idle interval.

Verify frozen controlled-fixture limits for CPU interval deltas and current RAM
values, and the separate cumulative peak-RAM ceiling. Verify no cgroup OOM kill.

A calibration run may propose limits but does not pass or change the frozen
limits. The test uses neither the opt-in profiler nor a production diagnostic
endpoint.

### Performance gates and reporting

- Preserve the existing latency and throughput assertions.
- Record every measured limit, value, fixture size, image, and phase.

### View result lifecycle

Rerun one View and remove it. Confirm each rerun drops the previous result
immediately.

After removal, confirm the result is unpinned and remains only while younger
than the configured TTL; after TTL cleanup, confirm no result table or pin
remains.

Keep an anchor View open beyond the short fixture TTL and verify its owned
result table remains available. Closing that View releases its pin; only after
TTL cleanup must its table disappear.
