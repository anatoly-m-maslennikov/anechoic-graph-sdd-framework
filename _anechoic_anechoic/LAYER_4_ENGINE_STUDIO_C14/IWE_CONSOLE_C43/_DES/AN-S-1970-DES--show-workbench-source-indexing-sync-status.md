---
atom_family: SPEC
atom_id: AN-S-1970
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: active
  version: 6
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Show Workbench source indexing sync status

## Claim

### Prose Claim

Expose source-to-DuckDB indexing status, not query execution/autosave: `syncing: true` during initial/refresh capture; `last_synced_at` only after successful reconciliation commits or confirms current committed state; failure preserves prior timestamp/error state; before first success timestamp is null. The shared MCP and HTTP status includes boolean `syncing`, null-or-offset/UTC `last_synced_at`, loaded Archive Scope Unit and Role pairs, and current audit state. Apply the selected Project binding and applicable exclusions.

Read an owner-local snapshot without long lifecycle/query lock, owner start, indexing, SQL or restart, so status remains observable during work. Set syncing before attempt and clear after; unchanged signature may confirm state without a new database write. Uninitialized owner returns false/null. Existing frontend polling renders compact top-right text and local browser time. Add no service, stream, queue, scheduler, retry or automatic restart.
