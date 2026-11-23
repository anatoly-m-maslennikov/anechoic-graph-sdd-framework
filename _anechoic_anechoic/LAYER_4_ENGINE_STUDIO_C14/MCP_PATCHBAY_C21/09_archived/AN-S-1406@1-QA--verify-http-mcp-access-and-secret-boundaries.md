---
atom_family: SPEC
atom_id: AN-S-1406
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-09 00:42:28 +0000
---
## Summary

verify HTTP MCP access and secret boundaries

# Summary

verify HTTP MCP access and secret boundaries

## Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

## Claim

the Evaluation **must** verify that HTTP access failures occur before MCP handling and preserve the existing permission and secret boundaries.

## Details

1. include good Requests and missing, wrong and changed Token cases, hostile Host/Origin cases, absent Origin, and authenticated Session continuations.
2. verify authentication rejection, SDK Host/Origin rejection and no Tool invocation or reload receipt on rejected Requests.
3. verify missing or invalid configuration prevents readiness; token rotation requires an explicit service restart and invalidates the previous Token.
4. check localhost-only Compose mapping, no Docker socket, no baked Token, no secret-bearing command arguments or logs, and unchanged stdio/default worker startup.
