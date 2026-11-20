---
atom_family: TKT
atom_id: AN-T-2044
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:49:20.652981+00:00'
---
## Summary

Engine replacements stage beneath the runtime directory

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/project_mcp_bootstrap.py`, `deploy_project_mcp_bootstrap`, stages replacement bootstrap files under `.anechoic_runtime`. `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMPILE_APPLICABLE_METHODOLOGY/compile_applicable_methodology.py`, `stage_outputs`, also puts replacement staging beneath `.anechoic_runtime`. Both are used by Local Release. CA-M-422@13 requires atomic replacement staging under Project `.anechoic_tmp` with a same-filesystem check. These paths use a different staging location.
