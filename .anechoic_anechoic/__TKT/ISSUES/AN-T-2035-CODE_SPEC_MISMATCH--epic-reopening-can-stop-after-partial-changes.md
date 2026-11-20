---
identity:
  atom_id: AN-T-2035
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:43:40.704324+00:00'
---
## Summary

Epic reopening can stop after partial changes

## Claim

### Prose Claim

In the ANECHOIC working tree based on commit `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/status_cascade.py`, `_plan`, checks a reopening child's source and allowed Status. It derives that child's final destination later during `_apply_one`. `_apply_one` converts placement ValueError to a generic `cascade_failed`.

On 12 November 2026, reopening CA-P-2791@46 activated the parent and 58 descendants, then stopped at Work Report CA-P-2964@1 with 67 Actions unrun. The tool reported 518 completed carrier effects. The failed report's Summary contains `query_run`, which `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/placement.py`, `_slug`, rejects. CA-O-10011@4 requires parent-first reopening and reporting the failed Action, reason, effects and unrun Actions. The ledger preserved the partial outcome. Its reason gave no actionable placement detail.
