---
atom_family: SPEC
atom_id: AN-S-3908
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 11
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

reuse the hot-reload Gateway for HTTP

# Summary

reuse the hot-reload Gateway for HTTP

## Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

## Claim

the HTTP transport implementation **must** reuse the Gateway's existing server handlers and generation lifecycle, so transport selection does not independently redefine Tool behavior.

## Details

1. factor one server-construction boundary for stdio and HTTP; keep implementation generations on their existing subprocess stdio connection.
2. use the installed MCP SDK's Streamable HTTP ASGI application and forward its lifespan; preserve stateful Sessions and the existing reload notifications.
3. close HTTP Sessions and all Gateway generations on shutdown. Do not replay interrupted Tool calls during reload or shutdown.
