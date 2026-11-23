---
atom_family: SPEC
atom_id: AN-S-2917
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 14:23:38 +0400
---

## Summary

Use Codex app-server for Workbench chat

## Claim

### Prose Claim

Use the official Codex app-server as the Workbench chat integration. Run it as a host process outside Docker. The browser connects through HTTP and SSE to a loopback host bridge on an OS-assigned port. The bridge connects to the installed app-server through stdio JSON-RPC and passes the explicit `project_root` only to ANECHOIC requests.

Allow the bridge's browser origin only from the selected Project MCP endpoint's exact scheme, host and port. Do not use wildcard CORS. Use the existing signed-in local Codex session. Do not mount Codex credentials into Docker. Reuse normal Codex model, authentication, sandbox and approval settings; provide no model picker and no special restricted environment.

Render the conversation in the existing Svelte Workbench panel. Start the bridge alongside the local-release MCP start path. Do not introduce a generic service framework.

Inherit enabled MCP servers from the local Codex configuration. For ANECHOIC, use the generated root `discover_tools` catalog and its current native MCP frontier. For other enabled MCP servers, use native discovery. Do not duplicate the server registries, limit them to Workbench Tools, or build a unified Tool registry.

Keep the native app-server thread as the Workspace's only conversation history. Store only its thread ID in a Workbench runtime state file. Serve that state through a same-origin Workbench route.
