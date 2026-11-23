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
  version: 13
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

verify HTTP MCP Gateway and stdio preservation

## Claim

### Prose Claim

the Evaluation **must** verify that real MCP HTTP initialization, discovery, calls and reload use the existing Gateway without breaking stdio behavior.

## Details

### Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

Use real-Gateway E2E fixtures with a disposable mock implementation to exercise Streamable HTTP initialization, discovery and a Tool call. Reload the mock on the same HTTP connection, verify the new registry/result, and keep an in-flight old-generation call until it drains. On lifespan exit, verify Session and generation cleanup; run existing stdio hot-reload tests unchanged. When Docker is available, verify the Docker service’s localhost URL in a container; a mock or host-ASGI pass does not satisfy that Docker gate.
