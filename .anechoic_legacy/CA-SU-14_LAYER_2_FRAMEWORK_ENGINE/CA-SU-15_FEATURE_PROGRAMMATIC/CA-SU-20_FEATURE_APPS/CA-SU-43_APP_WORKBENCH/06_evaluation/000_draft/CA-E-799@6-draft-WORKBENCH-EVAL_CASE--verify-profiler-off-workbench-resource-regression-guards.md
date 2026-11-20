---
identity:
  atom_id: CA-E-799
  ref_id: CA-E-799@6-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Performance <+ Measurement and Profiling
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 6
relations:
  evaluation_for:
  - CA-M-508
  - CA-R-2723
  IS_REPLACEMENT_FOR:
  - CA-E-799
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T01:09:16.497563+00:00'
destination:
  file:
    name: CA-E-799@6-draft-WORKBENCH-EVAL_CASE--verify-profiler-off-workbench-resource-regression-guards.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
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
