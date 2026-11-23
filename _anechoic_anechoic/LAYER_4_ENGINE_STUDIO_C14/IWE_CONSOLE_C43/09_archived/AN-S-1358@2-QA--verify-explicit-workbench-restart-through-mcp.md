---
atom_family: SPEC
atom_id: AN-S-1358
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Verify explicit Workbench restart through MCP

## Claim

An explicit MCP Workbench restart returns only after a fresh owner is ready, clears old query-result IDs, preserves sources and saved items, and leaves the MCP session and unrelated services usable. Invalid startup returns an explicit error and does not trigger automatic recovery.

## Details

| Scenario | Expected outcome |
| --- | --- |
| Run, save a query, restart, query again through one MCP session | Restart succeeds; fresh queries work; old Page ID is rejected; saved SQL still loads. |
| Scope Unit Declaration becomes invalid | Workbench reports unavailable. A restart while the Declaration is still invalid fails explicitly. |
| Declaration is corrected after that failure | It stays unavailable until explicit restart; restart then succeeds and reads corrected sources. |
| Another Workbench call is in flight | Restart waits for that call before closing its owner; no call uses a closed owner. |
| Request is cancelled while its synchronous work is in flight | Restart cannot close that owner until the synchronous work finishes. |
| Unexpected restart arguments | Rejected before a service effect. |
| Other MCP tools and source files | The same MCP session remains usable; source bytes and saved-item history remain unchanged. |
