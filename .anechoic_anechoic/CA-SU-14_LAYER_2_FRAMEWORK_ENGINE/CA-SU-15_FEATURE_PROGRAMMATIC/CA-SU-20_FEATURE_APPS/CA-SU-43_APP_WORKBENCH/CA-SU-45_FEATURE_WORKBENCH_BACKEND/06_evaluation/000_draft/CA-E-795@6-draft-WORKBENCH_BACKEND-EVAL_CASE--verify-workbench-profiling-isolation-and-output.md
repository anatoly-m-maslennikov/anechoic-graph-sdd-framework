---
identity:
  atom_id: CA-E-795
  ref_id: CA-E-795@6-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Performance <+ Measurement and Profiling
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2998
  - CA-M-525
  IS_REPLACEMENT_FOR:
  - CA-E-795
state:
  status: draft
  version: 6
  updated_at: '2026-11-13T20:47:48.790558+00:00'
destination:
  file:
    name: CA-E-795@6-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-workbench-profiling-isolation-and-output.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify Workbench profiling isolation and output

## Claim

### Prose Claim

Run the profiler through the actual DuckDB/DuckPGQ path on a small valid disposable Project. Verify readable cProfile statistics, nonempty allocation diagnostics, dataset and cycle counts, explicit instrumented labels, correct RSS and native-memory labels, and identical source hashes before and after the run.

Verify that output stays beneath the selected Project temporary root. Bounded cleanup removes the disposable database or reports its confined retained path without retrying or losing the original failure.

Run normal performance gates without cProfile or tracemalloc. Profiler duration must not satisfy latency or throughput assertions.
