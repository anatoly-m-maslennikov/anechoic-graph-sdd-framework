---
identity:
  atom_id: AN-T-2040
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:48:57.188890+00:00'
---
## Summary

Single Change Status returns a workflow ledger

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/registry_lifecycle_provider.py`, `_result`, includes the Workflow binding, Run ID, Action results, artifact and effects when a successful Change Status response has a Workflow binding. `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/status_cascade.py` supplies that binding for a single leaf as well as a cascade. CA-R-1105@31 limits successful single-Atom lifecycle responses to Status. The public response contains more fields even for the leaf case.
