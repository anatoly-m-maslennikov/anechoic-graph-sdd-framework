---
atom_family: SPEC
atom_id: AN-S-1406
container:
  component: C21
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

verify HTTP MCP access and secret boundaries

## Claim

### Prose Claim

the Evaluation **must** verify that HTTP access failures occur before MCP handling and preserve the existing permission and secret boundaries.

## Details

### Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

1. include good Requests with absent, valid-looking, and arbitrary Authorization values, hostile Host/Origin cases, absent Origin, and Session continuations.
2. verify Host/Origin rejection and no Tool invocation or reload receipt on rejected Requests; Authorization values do not grant, deny, or otherwise alter admitted localhost access.
3. verify readiness requires the loopback Host/Origin and MCP initialization boundary, not password, bearer, Token, credential configuration, or rotation.
4. check localhost-only Compose mapping, no Docker socket, no HTTP credential configuration, no secret-bearing command arguments or logs, and unchanged stdio/default worker startup.
