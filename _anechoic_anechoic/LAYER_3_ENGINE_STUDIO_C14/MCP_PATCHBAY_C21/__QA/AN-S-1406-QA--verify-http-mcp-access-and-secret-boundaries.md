---
atom_family: SPEC
atom_id: AN-S-1406
structure:
  container:
    component: C21
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 12
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

verify HTTP MCP access and secret boundaries

## Claim

### Prose Claim

the Evaluation **must** verify that HTTP access failures occur before MCP handling and preserve the existing permission and secret boundaries.

## Details

### Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

Exercise absent, valid-looking and arbitrary Authorization values; hostile Host/Origin cases; absent Origin; and Session continuations. Rejected Host/Origin requests must invoke no Tool and produce no reload receipt; Authorization neither changes localhost admission nor supplies authority. Verify readiness depends on loopback Host/Origin and MCP initialization, not password, bearer, Token, credential configuration or rotation. Check loopback-only Compose mapping, no Docker socket or HTTP credential configuration, no secret-bearing arguments/logs, and unchanged stdio/default worker startup.
