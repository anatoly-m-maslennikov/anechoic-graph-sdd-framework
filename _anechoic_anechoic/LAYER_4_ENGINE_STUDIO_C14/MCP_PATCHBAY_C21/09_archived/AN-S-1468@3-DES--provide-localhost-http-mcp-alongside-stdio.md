---
atom_family: SPEC
atom_id: AN-S-1468
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

provide localhost HTTP MCP alongside stdio

# Summary

provide localhost HTTP MCP alongside stdio

## Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

## Claim

MCP **must** provide an explicitly started localhost HTTP endpoint alongside the existing stdio connection, exposing the same admitted Tool capabilities through the existing hot-reload Gateway.

## Details

1. keep stdio available with its current default behavior; HTTP is an additional transport, not another Tool registry or implementation server.
2. preserve generation routing, in-flight draining, reload control and truthful client-refresh status across HTTP calls.
3. starting the endpoint provides a capability; it does not start a Workflow or infer its completion.
