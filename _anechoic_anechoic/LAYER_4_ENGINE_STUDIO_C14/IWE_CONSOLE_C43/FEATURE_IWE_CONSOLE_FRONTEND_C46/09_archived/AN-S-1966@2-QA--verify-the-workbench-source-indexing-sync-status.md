---
atom_family: SPEC
atom_id: AN-S-1966
container:
  component: C46
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Verify the Workbench source indexing sync status

## Claim

### Prose Claim

Exercise the built Workbench against the real backend and its existing HTTP polling path. Verify the status text is a small top-right header element, uses browser-local time, and never confuses indexing with query execution or browser autosave.

| Case | Expected result |
| --- | --- |
| Initial source capture or a refresh is running | A poll observes `syncing: true`; the UI shows `Syncing` while queries and autosave remain separate states. |
| No successful capture/materialization commit has occurred | The payload has `last_synced_at: null`; the UI shows `Not synced yet`. |
| Capture/materialization reconciliation succeeds, with a new commit or unchanged committed state confirmed | A later poll shows `syncing: false` and an updated offset-bearing `last_synced_at`, rendered in the browser's local time. |
| Capture or materialization fails after a previous successful sync | `syncing` becomes false, the previous timestamp remains visible, and the existing failure state/error behavior remains; the UI does not claim a new sync or restart the owner. |
| Status is polled during a long indexing operation | The status response remains observable without waiting for the long lifecycle/query lock. |
| A query runs, completes, or the browser autosaves a View | The sync text and timestamp do not change unless source-to-DuckDB indexing successfully reconciles its sources. |
| HTTP `POST /anechoic/workbench/<project_name>/status` and MCP `workbench_status({})` reads are compared | Both expose exactly `syncing` and `last_synced_at` with the same semantics; no error field, new event stream or service is required. |

Use the real browser flow and backend; assert visible text and response behavior rather than component internals. Verify the existing polling mechanism is reused and no automatic restart is triggered.
