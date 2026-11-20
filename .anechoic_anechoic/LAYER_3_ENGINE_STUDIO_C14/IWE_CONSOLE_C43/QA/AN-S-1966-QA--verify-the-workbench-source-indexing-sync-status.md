---
identity:
  atom_id: AN-S-1966
context:
  container:
    component: C43
  tier: 5
  lens: QA
state:
  status: active
  version: 5
  updated_at: '2026-11-12T16:59:40.785330+00:00'
---
## Summary

Verify the Workbench source indexing sync status

## Claim

### Prose Claim

Use built browser/real backend existing HTTP polling. Verify small top-right local-time text distinguishes indexing from query/autosave: initial/refresh poll sees `syncing: true`/Syncing; before success false/null shows Not synced yet; successful commit or confirmed committed state shows false/new offset timestamp; failure preserves prior timestamp/error and does not claim sync/restart. Status remains observable during long indexing. Query/autosave never changes it. Compare shared Project API, legacy Workbench alias and MCP status. Verify identical sync state, Archive coverage and audit state for the same Project. Reject mismatched Project binding. Assert visible controls/responses, reuse polling and no automatic restart.
