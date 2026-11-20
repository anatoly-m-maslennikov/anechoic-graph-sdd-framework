---
identity:
  atom_id: AN-S-2920
context:
  container:
    component: C48
  tier: 4
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

`FEATURE_CODEX_EXTENSION` instructions **must** direct the caller to invoke `workspace_open` with the host-supplied session ID and trusted Project root. Its hook supplies context only, starts nothing, and registers no panel; `plugin.json` adds no panel or connection declaration. The existing `anechoic-workbench` package **must** be registered in `.agents/plugins/marketplace.json` under `anechoic-local` with local source `./LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_CODEX_EXTENSION/plugin`. The desktop app discovers it after restart and the Operator installs it and explicitly trusts the bundled hook through `/hooks`. Activation requires a new or resumed native chat; building or releasing the backend neither installs the plugin nor retroactively runs a hook.
