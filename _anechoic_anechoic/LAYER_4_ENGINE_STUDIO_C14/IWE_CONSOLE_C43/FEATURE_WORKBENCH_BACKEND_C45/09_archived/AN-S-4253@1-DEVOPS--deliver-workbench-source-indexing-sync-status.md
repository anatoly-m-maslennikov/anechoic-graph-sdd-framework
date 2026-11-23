---
atom_family: SPEC
atom_id: AN-S-4253
container:
  component: C45
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 19:04:52 +0400
---
## Summary

Deliver Workbench source indexing sync status

## Claim

### Prose Claim

Deliver native MCP `workbench_status({})` and the matching read-only `POST /anechoic/workbench/<project_name>/status` connector with `{}` (plus the trusted `project_root` envelope in shared mode). Register it through the grouped Service catalog and keep the normal blacklist and selected-root validation. Return exactly `syncing` (boolean) and `last_synced_at` (ISO-8601 UTC or offset-bearing timestamp, or `null` before the first successful reconciliation). Do not add an error field; the existing error boundary remains. The status is source capture-to-DuckDB indexing state, not query execution or browser autosave.

The response remains available while a capture or materialization operation is running and must not wait for the long lifecycle or query lock, start an uninitialized owner, execute SQL, or restart a failed owner. A successful capture/materialization reconciliation turns `syncing` off and advances `last_synced_at`; it may reuse unchanged committed DuckDB state without a new database write. A failed run keeps the previous timestamp and existing failure state. The frontend may poll it through its existing interval. Do not deliver a new service, event stream, scheduler, retry or restart workflow.
