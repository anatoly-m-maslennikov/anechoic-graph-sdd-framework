---
identity:
  atom_id: AN-S-1966
context:
  container:
    component: C43
  tier: 5
  lens: QA
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T00:32:29.280634+00:00'
---
## Summary

Verify the Workbench source indexing sync status

## Claim

### Prose Claim

Verify the Workbench source indexing sync status in the built browser with
the real backend and its existing HTTP polling.

## Details

- Check visible controls and responses during long indexing.
- Query execution and autosave leave sync status unchanged.
- Verify that polling never restarts Workbench automatically.

### Status text

- The small top-right text uses local time.
- Initial indexing or refresh shows Syncing with `syncing: true`.
- Before the first success, false and a null timestamp show Not synced yet.
- A successful commit or confirmation shows false and a new offset timestamp.
- Failure preserves the prior timestamp and error. Polling reports no success.

### Status interfaces

- Compare the Project API, legacy Workbench URL, and MCP for the same Project.
  Sync state, Archive coverage, and audit state must match.
- Reject a mismatched Project binding.
