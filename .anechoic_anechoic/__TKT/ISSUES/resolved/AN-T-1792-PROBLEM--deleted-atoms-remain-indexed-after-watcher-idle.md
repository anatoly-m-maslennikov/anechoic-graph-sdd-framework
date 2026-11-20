---
identity:
  atom_id: AN-T-1792
context:
  container:
    component: C14
  tier: 3
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-11-11 03:05:37 +0400
---

## Summary

Deleted Atoms remain indexed after watcher idle

## Concern

After the C707 batch updated ten Current Atoms and removed two Current Method carriers and their owned Drafts, query_run still returned M417/M426 as Current although their source paths were absent and workbench_status reported syncing=false. A full Workbench reread removed both rows.

## Details

Reproduce the mixed update/delete batch and correct the incremental indexing path. Do not infer the internal cause from this observation. Preserve actual deletion semantics and add coverage through the existing watcher Evaluation E677. Source retirement was independently verified after the reread; this Problem remains Active until the code fix and acceptance are verified.


## Resolution

Verified on the running 0.4.4.40 image (c6e5cfb3e431) on 11 November 2026. The retained real-project mixed canary updates ten Current Atoms and removes two Current Methods and their two numbered Drafts. All ten updated rows were visible and all four deleted rows absent while syncing=false, without reread, in 0.284 s from the start of mutation. Owned source and index cleanup passed.

The current delta implementation unions old/new carrier keys, deletes the previous rows and inserts surviving replacements in one transaction. Existing direct and polling-watcher integration tests cover the mixed shape; the live image adds native-watcher acceptance. No additional runtime patch was needed to pass this reproduction; the original older runtime's internal cause remains unproven. This resolves the observed stale-row behavior, not unrelated model admission or general performance acceptance.

Evidence: .anechoic_tmp/CA-P-2791/CA-P-2813/live-mixed-canary/mixed-latest.json and mixed-live-corrected-timings.log. Retained test: test_workbench_live_mixed_canary.py.
