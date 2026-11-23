---
atom_family: SPEC
atom_id: AN-S-1966
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify the Workbench source indexing sync status

## Claim

### Prose Claim

Use built browser/real backend existing HTTP polling. Verify small top-right local-time text distinguishes indexing from query/autosave: initial/refresh poll sees `syncing: true`/Syncing; before success false/null shows Not synced yet; successful commit or confirmed committed state shows false/new offset timestamp; failure preserves prior timestamp/error and does not claim sync/restart. Status remains observable during long indexing. Query/autosave never changes it. Compare HTTP POST and MCP reads: exactly `syncing` and `last_synced_at`, same semantics, no error field/stream/service. Assert visible controls/responses, reuse polling and no automatic restart.
