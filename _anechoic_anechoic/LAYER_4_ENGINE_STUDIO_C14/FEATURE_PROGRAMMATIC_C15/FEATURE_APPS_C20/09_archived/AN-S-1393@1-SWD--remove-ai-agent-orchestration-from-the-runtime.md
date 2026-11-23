---
atom_family: SPEC
atom_id: AN-S-1393
container:
  component: C20
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-07 04:18:21 +0400
---

## Summary

Remove AI Agent orchestration from the runtime

## Claim

### Prose Claim

Remove automatic AI Agent dispatch and its Codex CLI adapters, transport, mock runners, agentic handlers, Docker service and credentials setup. Keep the general Workflow engine, durable queue, deterministic Action handlers, MCP, Workbench and host Release commands. Retain RMED source Atoms and persisted historical Run data. A request requiring removed Agent execution must stop with an explicit unsupported result before it is queued or starts effects; never substitute a mock Agent.
