---
atom_family: TKT
atom_id: AN-T-2048
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:53:23.967662+00:00'
---
## Summary

Archive loading and sync status drift from the public contract

## Claim

### Prose Claim

CA-D-718@1 names `/api/archive-load` below the Project page. `FEATURE_MCP/workbench_web.py` and the browser transport both use `/archive-load`. CA-R-2952@4 and CA-E-781@4 require a two-field status response, while CA-D-715@3 and CA-D-718@1 require additional audit and Archive coverage fields. `FEATURE_WORKBENCH_BACKEND/service.py` returns the additive shape. Consumers following the route stated in the Delivery cannot invoke Archive loading through it.
