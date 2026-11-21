---
atom_family: TKT
atom_id: AN-T-2038
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-21T00:53:58.174208+00:00"
---
## Summary

Workbench reread loses loaded Archive coverage

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_tools.py` replaces the Workbench service in its reread operation. The replacement starts with empty loaded Archive coverage in `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service.py`. Previously loaded Archived rows therefore disappear after reread until the caller loads the scopes again. CA-R-2786@5 and CA-E-677@30 require reread to retain the selected Archive coverage while rebuilding derived data under the installed schema.
