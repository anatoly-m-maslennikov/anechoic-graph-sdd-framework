---
atom_family: SPEC
atom_id: AN-S-1972
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 2
  updated_at: '2026-11-12T17:03:37.731536+00:00'
---
## Summary

Reuse one Gateway for HTTP and stdio

## Claim

### Prose Claim

Use the same MCP Gateway handlers and Tool registration for HTTP and stdio. The installed runtime provides one set of Tool behavior for both transports.

## Details

Use the installed MCP SDK’s Streamable HTTP application for HTTP Sessions. Close Sessions on shutdown. Apply code and compiled contract changes by starting a rebuilt runtime under CA-M-551.

For a saved Bookmark or View, derive its URL from the bound HTTP request when available. For stdio, use the bound Project's optional `workbench.public_url` in `.anechoic_runtime/anechoic_runtime_settings.toml`. It identifies the absolute HTTP or HTTPS Workbench page for that Project. If the URL is unavailable, return the saved ID with `saved_query_url: null` and `saved_query_url_reason: workbench_url_unknown`. Saving remains successful and the saved ID remains usable. Use the same rule for saved-item lists.
