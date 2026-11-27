---
atom_family: SPEC
atom_id: AN-S-1392
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 15
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---

## Summary

bound localhost HTTP MCP Requests

## Claim

### Prose Claim

the HTTP access implementation **must** validate the loopback Host/Origin boundary before the existing MCP handlers receive a Request, without password, bearer, or other HTTP authentication.

## Details

### Localhost transport boundary

1. Use a narrow ASGI loopback Host/Origin guard for every HTTP Request, including Session continuations; forward lifespan unchanged.
2. Enable MCP SDK DNS-rebinding protection explicitly; a container bind address of 0.0.0.0 does not disable validation.
3. Do not read, require, validate, rotate, inject, or report HTTP password, bearer Token, Authorization, or credential configuration; such a header cannot alter admitted localhost access.
4. Health checks and host-side MCP initialization use the same boundary and report readiness without starting a Workflow.

This Method replaces CA-M-342, whose fixed Summary identifies the retired bearer-authentication procedure.
