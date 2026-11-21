---
atom_family: SPEC
atom_id: AN-S-1369
structure:
  container:
    component: C45
  tier: 6
context:
  lens: QA
state:
  status: active
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify the deployed MCP Workbench query schema.

## Claim

### Prose Claim

Verify the deployed MCP query schema requires `sql` and accepts optional native-typed `preview` (non-negative integer) and `save` (boolean). A native SDK request with `preview: 0` and `save: false` reaches the operation, yields the expected zero-row preview and creates no saved query; shared results/saved-resource behavior remains consistent.
