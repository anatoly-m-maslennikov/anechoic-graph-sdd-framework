---
atom_family: SPEC
atom_id: AN-S-4259
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Retain a non-blocking Workbench source indexing status

## Claim

### Prose Claim

Keep a small owner-local status snapshot beside the existing Workbench indexing state. Set `syncing` before initial capture or refresh begins and clear it when that attempt finishes. Advance `last_synced_at` only after capture/materialization reconciliation succeeds and the existing committed DuckDB state is current; when the source signature is unchanged, reuse that committed state without forcing a new database write. Record the timestamp as an offset-bearing value. On failure, preserve the previous timestamp and retain the existing failure state and error boundary.

Read the snapshot without waiting on the long lifecycle, refresh or query lock, without triggering owner start, indexing, query execution or restart. This lets a status request observe `syncing: true` while a long initial or refresh operation is running. An uninitialized owner returns the same shape with `syncing: false` and `last_synced_at: null`; the existing owner lifecycle remains responsible for starting Workbench operations.

Expose the same read-only status contract through the native MCP surface and its matching HTTP adapter, using the existing discovery/catalog and parity pattern. The payload is exactly `syncing` and `last_synced_at`. Reuse the existing frontend polling interval. Do not add a watcher service, event stream, scheduler, retry loop, or automatic restart.
