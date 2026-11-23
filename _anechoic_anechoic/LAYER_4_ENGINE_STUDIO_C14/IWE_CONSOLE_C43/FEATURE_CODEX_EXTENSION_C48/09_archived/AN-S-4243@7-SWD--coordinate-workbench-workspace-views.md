---
atom_family: SPEC
atom_id: AN-S-4243
container:
  component: C48
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 7
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Coordinate Workbench Workspace Views

## Claim

### Prose Claim

Use the existing Codex chat as the native Workspace boundary and the existing `workspace_open` MCP operation as the native UI activation. Its host tool input is the sole native identity source: accept only non-empty `session_id` and explicit trusted `project_root`, and accept its initial structured result as the opened Workspace. Do not read URL parameters or localStorage in native mode, manufacture a native session, bind another Workspace, or call `workspace_open` a second time. Missing input or result is a visible binding error and makes no backend call.

Use one shared Svelte Workbench UI. Native bootstrap uses MCP Apps initialization and the `tools/call` bridge; it injects the explicit `project_root` into every call, preserves `structuredContent`, and rejects `isError`. It adds no domain logic, response adapter, MCP service, chat, or UI-specific handler.

The initial native Workspace result carries the selected Project's canonical project_name. Reuse the existing ProjectSelection settings/name reader at the public adapter boundary. Keep this derived name out of persisted Workspace documents and do not infer it from a directory basename or add a query, parser, fallback name, or tool. The native frontend uses that supplied name for its Project header.
