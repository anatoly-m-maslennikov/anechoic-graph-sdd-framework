---
atom_family: SPEC
atom_id: AN-S-3455
container:
  component: C21
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-10-09 00:42:28 +0000
---
## Summary

authenticate and bound HTTP MCP Requests

# Summary

authenticate and bound HTTP MCP Requests

## Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

## Claim

the HTTP access implementation **must** validate the bearer Token and loopback Host/Origin boundary before the existing MCP handlers receive a Request.

## Details

1. use a narrow ASGI bearer guard with constant-time comparison for every HTTP Request, including Session continuations. Forward lifespan unchanged.
2. enable the MCP SDK's DNS-rebinding protection explicitly; a container bind address of `0.0.0.0` does not disable Host/Origin validation.
3. a fixed local Token does not require an OAuth issuer. Obtain its value from the admitted runtime environment and expose no secret in failures.
4. health checks use the same authenticated endpoint and report readiness without running a Workflow or printing a Token.

## Lineage

replaced by CA-M-357, which defines the password-free localhost HTTP boundary.
