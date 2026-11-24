---
atom_family: SPEC
atom_id: AN-S-1924
container:
  component: C21
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: '2026-11-12T01:59:14.433341+00:00'
---
## Summary

verify HTTP MCP Gateway and stdio preservation

## Claim

### Prose Claim

the Evaluation **must** verify that real MCP HTTP initialization, discovery and calls use the existing Gateway without breaking stdio behavior.

## Details

### Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

Use real-Gateway E2E fixtures with a disposable mock implementation to exercise Streamable HTTP initialization, discovery and a Tool call. On lifespan exit, verify Session cleanup; run existing stdio transport tests. When Docker is available, verify the Docker service’s localhost URL in a container; a mock or host-ASGI pass does not satisfy that Docker gate.
