---
atom_family: SPEC
atom_id: AN-S-2920
structure:
  container:
    component: C48
  tier: 4
context:
  lens: DevOps
state:
  status: draft
  version: 1
  updated_at: 2026-11-10 06:28:05 +0400
---

## Summary

Deliver the native Workbench MCP App

## Claim

### Prose Claim

The shared Svelte Workbench UI **must** use MCP Apps initialization and the `tools/call` bridge in native mode. It **must** inject the explicit `project_root` into every call, preserve `structuredContent`, reject `isError`, and add no domain logic, response adapter, MCP service, chat, or UI-specific handler. Standalone mode retains the existing HTTP bootstrap; native mode and standalone mode use the same `App.svelte` and Workbench backend.

`workspace_open` is the sole UI-bearing MCP tool. Its descriptor **must** link `ui://anechoic/workbench.html`, served as `text/html;profile=mcp-app`. `workbench_app.html` **must** be one self-contained MCP App resource built with the existing Vite/Svelte toolchain: its JavaScript and CSS are inline, it opens no browser, makes no Workbench HTTP request, and needs no second server. `FEATURE_MCP` adds that resource URI only to the existing `workspace_open` descriptor and serves the built resource through its existing registry/read handler; existing dispatch, Project validation, and structured-result paths remain unchanged.
