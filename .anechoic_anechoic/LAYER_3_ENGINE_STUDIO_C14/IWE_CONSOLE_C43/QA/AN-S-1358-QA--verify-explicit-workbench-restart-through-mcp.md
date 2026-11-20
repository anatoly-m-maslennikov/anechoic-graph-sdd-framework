---
identity:
  atom_id: AN-S-1358
context:
  container:
    component: C43
  tier: 5
  lens: QA
state:
  status: active
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify explicit Workbench restart through MCP

## Claim

### Prose Claim

Verify explicit MCP restart waits for fresh owner readiness, invalidates old result IDs, preserves sources/saved items and leaves session/unrelated services usable; invalid startup errors without recovery. In one session, Run/save/restart/query: fresh queries work, old Page ID rejects and saved SQL loads. Verify invalid Declaration remains unavailable until corrected then explicitly restarted; in-flight/cancelled work prevents closing its owner; bad arguments reject before effect; source bytes/history/MCP tools remain usable.
