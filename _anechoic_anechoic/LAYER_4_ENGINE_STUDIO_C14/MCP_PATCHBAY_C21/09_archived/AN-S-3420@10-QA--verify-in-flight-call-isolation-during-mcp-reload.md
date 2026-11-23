---
atom_family: SPEC
atom_id: AN-S-3420
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-11-07 04:28:07 +0400
---
## Summary

Verify in-flight call isolation during MCP reload

# Summary

Verify in-flight call isolation during MCP reload

## Scope

These in-flight generation checks apply only with optional hot reload explicitly enabled.

server-side hot reload for the Project-local MCP gateway.

## Claim

the MCP Evaluation **must** verify that reload preserves admitted call identity, authority **and** truthful outcomes.

## Details

- hold a call on A while publishing B; verify that the old call completes on A **and** a new call executes on B.
- verify that old generations remain alive while their admitted calls are running.
- simulate child-process failure **after** a mutating call starts; verify an explicit uncertain outcome **and** no automatic replay.
- exercise concurrent reload requests, duplicate request IDs **and** drain limits; verify serialized publication **and** bounded explicit diagnostics.
- verify that reload does **not** start a Workflow, Codex Agent, independent worker **or** source mutation.
- verify that get_mcp_reload_status advertises read-only metadata **and** returns generation state without reload **or** persistence.
- verify that reload_mcp_implementation remains state-changing, rejects operation status **and** does **not** alter client permission settings.
- retain existing MCP request validation **and** Project-boundary regression tests.
