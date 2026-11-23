---
atom_family: SPEC
atom_id: AN-S-1970
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Show Workbench source indexing sync status

## Claim

### Prose Claim

Expose source-to-DuckDB indexing status, not query execution/autosave: `syncing: true` during initial/refresh capture; `last_synced_at` only after successful reconciliation commits or confirms current committed state; failure preserves prior timestamp/error state; before first success timestamp is null. Payload is exactly boolean `syncing` and null-or-offset/UTC `last_synced_at`, over native `workbench_status({})` and matching read-only POST status connector, with normal selected-root/blacklist validation and no error field.

Read an owner-local snapshot without long lifecycle/query lock, owner start, indexing, SQL or restart, so status remains observable during work. Set syncing before attempt and clear after; unchanged signature may confirm state without a new database write. Uninitialized owner returns false/null. Existing frontend polling renders compact top-right text and local browser time. Add no service, stream, queue, scheduler, retry or automatic restart.
