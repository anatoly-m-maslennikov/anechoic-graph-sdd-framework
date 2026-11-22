---
atom_family: TKT
atom_id: AN-T-2040
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:54:06.815558+00:00'
---
## Summary

Single Change Status returns a workflow ledger

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/registry_lifecycle_provider.py`, `_result`, includes the Workflow binding, Run ID, Action results, artifact and effects when a successful Change Status response has a Workflow binding. `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/status_cascade.py` supplies that binding for a single leaf as well as a cascade. CA-R-1105@31 limits successful single-Atom lifecycle responses to Status. The public response contains more fields even for the leaf case.
