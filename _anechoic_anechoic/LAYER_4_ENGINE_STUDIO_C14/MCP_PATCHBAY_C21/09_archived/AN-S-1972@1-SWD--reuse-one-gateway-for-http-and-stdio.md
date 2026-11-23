---
atom_family: SPEC
atom_id: AN-S-1972
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T01:59:14.433341+00:00'
---

## Summary

Reuse one Gateway for HTTP and stdio

## Claim

### Prose Claim

Use the same MCP Gateway handlers and Tool registration for HTTP and stdio. The installed runtime provides one set of Tool behavior for both transports.

## Details

Use the installed MCP SDK’s Streamable HTTP application for HTTP Sessions. Close Sessions on shutdown. Apply code and compiled contract changes by starting a rebuilt runtime under CA-M-551.
