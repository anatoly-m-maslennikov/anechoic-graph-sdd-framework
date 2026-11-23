---
atom_family: SPEC
atom_id: AN-S-1409
container:
  component: C20
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-07 04:18:21 +0400
---

## Summary

Verify the runtime without AI Agent orchestration

## Claim

### Prose Claim

Verify that MCP and Workbench start, deterministic Workflow handlers and the general queue remain available, and local/public Release commands still import. Verify that the image has no Codex CLI install, Agent service, credentials mount or Agent dependency. Verify that removed Agentic requests fail explicitly before queue admission, with no implicit Agent or mock execution. Run the retained runtime and Docker regression checks; preserve RMED and historical Run data.
