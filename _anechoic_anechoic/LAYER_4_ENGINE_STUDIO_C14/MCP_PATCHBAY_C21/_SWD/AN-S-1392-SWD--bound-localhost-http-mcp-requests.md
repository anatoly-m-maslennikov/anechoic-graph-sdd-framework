---
atom_family: SPEC
atom_id: AN-S-1392
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 16
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---

## Summary

bound localhost HTTP MCP Requests

## Claim

### Prose Claim

Apply AN-S-1388 to requests before they reach MCP handlers.

## Details

### Localhost transport boundary

1. Use a narrow ASGI loopback Host/Origin guard for every HTTP Request, including Session continuations; forward lifespan unchanged.
2. Enable MCP SDK DNS-rebinding protection explicitly; a container bind address of 0.0.0.0 does not disable validation.
3. An Authorization header does not alter admitted access.
4. Health checks and host-side MCP initialization use the same boundary and report readiness without starting a Workflow.

This Method replaces CA-M-342, whose fixed Summary identifies the retired bearer-authentication procedure.
