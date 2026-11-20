---
identity:
  atom_id: AN-S-1361
context:
  container:
    component: C43
  tier: 6
  lens: QA
state:
  status: active
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify profiler-off Workbench resource regression guards

## Claim

### Prose Claim

Run the existing disposable 5,000-Atom Workbench Docker fixture with `tracemalloc` and CPU profiling disabled. Take cgroup snapshots immediately before and after cold index, warm full reread and a true 15-second idle interval. Verify frozen controlled-fixture limits for those CPU interval deltas and current RAM values, plus the separate cumulative peak-RAM ceiling. Verify no cgroup OOM kill.

Run a bounded View lifecycle that reruns one View and removes it. Confirm each rerun drops the previous result immediately. After removal, confirm the result is unpinned and remains only while it is younger than the configured TTL; after TTL cleanup, confirm no result table or pin remains. Preserve the existing latency and throughput assertions unchanged.

## Details

Record every measured limit, value, fixture size, image and phase in test output. A calibration run may propose limits but does not pass or change the frozen limits. The test does not use the opt-in profiler or a production diagnostic endpoint.

Keep an anchor View open beyond the short fixture TTL and verify that its owned result table remains available. Closing that View releases its pin; only after TTL cleanup must its table disappear.
