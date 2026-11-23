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
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Show Workbench source indexing sync status

## Claim

### Prose Claim

The Workbench must expose whether source-to-DuckDB indexing is running and when it last completed successfully.

- During initial indexing or a source refresh, report `syncing: true`. The status describes source capture and DuckDB materialization, not query execution, browser autosave or another UI operation.
- Set `last_synced_at` only after a successful capture/materialization reconciliation has committed, or has confirmed the existing committed DuckDB state is current. Return it as a UTC or offset-bearing timestamp. A failed run keeps the previous timestamp and the existing source/indexing failure state.
- Before the first successful commit, return `last_synced_at: null`; the frontend displays `Not synced yet`.
- Provide the small read-only status payload over the existing HTTP and MCP parity surface. Its fields are `syncing` and `last_synced_at`. Do not restart a failed Workbench automatically.
- Poll this status through the existing frontend polling mechanism. Show a small status text at the top right and render a non-null timestamp in the browser's local time. Do not add a new service, event stream, queue or scheduler.
