---
identity:
  atom_id: AN-S-1358
context:
  container:
    component: C43
  tier: 5
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T20:47:27.713054+00:00'
---
## Summary

Verify explicit Workbench restart through MCP

## Claim

### Prose Claim

In one session, run and save a query, restart Workbench through MCP, and run a fresh query. Verify that restart waits for the fresh owner to be ready, the fresh query works, the old Page result ID is rejected, and the saved SQL loads. Verify that sources and saved items are preserved and that the session and unrelated services remain usable.

Verify that invalid startup returns an error without recovery. An invalid Declaration keeps Workbench unavailable until the Declaration is corrected and Workbench is explicitly restarted. In-flight or cancelled work prevents its owner from being closed. Invalid arguments are rejected before any effect. Verify that source bytes, history and MCP tools remain usable.
