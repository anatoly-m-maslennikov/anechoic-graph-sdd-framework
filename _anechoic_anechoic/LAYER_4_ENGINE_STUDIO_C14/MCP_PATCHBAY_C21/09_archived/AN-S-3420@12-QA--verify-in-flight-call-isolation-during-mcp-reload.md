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
  version: 12
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify in-flight call isolation during MCP reload

## Claim

### Prose Claim

the MCP Evaluation **must** verify that reload preserves admitted call identity, authority **and** truthful outcomes.

## Details

These in-flight generation checks apply only with optional hot reload explicitly enabled for the Project-local MCP gateway.

- Hold a call on A while publishing B; old call completes on A and a new call executes on B. Old generations remain alive while admitted calls run.
- Fail the child process after a mutating call starts; return an explicit uncertain outcome and never replay automatically.
- Exercise concurrent reloads, duplicate request IDs, and drain limits; verify serialized publication and bounded explicit diagnostics.
- Verify reload starts no Workflow, Codex Agent, independent worker, or source mutation; get_mcp_reload_status is read-only generation metadata with no reload/persistence; reload_mcp_implementation remains state-changing, rejects operation status, and does not alter client permission settings.
- Retain MCP request-validation and Project-boundary regression tests.
