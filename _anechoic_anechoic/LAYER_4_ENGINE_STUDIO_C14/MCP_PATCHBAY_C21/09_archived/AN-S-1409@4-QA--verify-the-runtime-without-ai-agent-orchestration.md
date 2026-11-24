---
atom_family: SPEC
atom_id: AN-S-1409
container:
  component: C21
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify the runtime without AI Agent orchestration

## Claim

### Prose Claim

Verify one MCP health/tool smoke, one successful Workbench query, and one successful deterministic Workflow run through the retained queue without an Agent dependency. Verify both host local/public Release entry points through their existing effect-free smoke/tests. Verify that the image has no Codex CLI install, Agent service, credentials mount or Agent dependency. Verify that removed Agentic requests fail explicitly before queue admission, with no new durable queue/Run record, mutation or implicit Agent/mock execution. Run the retained runtime and Docker regression checks; preserve RMED and historical Run data.
