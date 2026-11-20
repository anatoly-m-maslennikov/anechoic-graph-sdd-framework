---
identity:
  atom_id: AN-S-1468
context:
  container:
    component: C21
  tier: 3
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-11-11 06:09:13 +0400
---
## Summary

provide localhost HTTP MCP alongside stdio

## Claim scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

## Claim

### Prose Claim

MCP **must** provide an explicitly started localhost HTTP endpoint alongside the existing stdio connection, exposing the same admitted Tool capabilities through the existing Project MCP Gateway.

## Details

1. keep stdio available with its current default behavior; HTTP is an additional transport, not another Tool registry or implementation server.
2. preserve the fixed Project boundary and admitted Tool behavior across HTTP calls.
3. starting the endpoint provides a capability; it does not start a Workflow or infer its completion.
