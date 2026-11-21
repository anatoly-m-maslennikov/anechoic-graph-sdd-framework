---
atom_family: TKT
atom_id: AN-T-2046
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-21T00:54:32.781288+00:00"
---
## Summary

MCP sessions can share pending lifecycle corrections

## Claim

### Prose Claim

CA-M-167@26 binds pending lifecycle corrections to the same Project, client session and Tool. CA-M-517@1 supplies the generic caller session ID. In `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/registry_lifecycle_provider.py`, the pending input key uses the transport Connection, Project and Tool. A local probe put two generic sessions on one Connection. The second caller completed the first caller’s partial Create Draft request. The probe performed no writes.
