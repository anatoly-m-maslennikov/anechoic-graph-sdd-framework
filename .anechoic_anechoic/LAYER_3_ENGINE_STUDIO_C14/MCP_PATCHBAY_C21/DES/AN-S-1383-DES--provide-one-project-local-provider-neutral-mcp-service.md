---
identity:
  atom_id: AN-S-1383
context:
  container:
    component: C21
  tier: 1
  lens: DES
state:
  status: active
  version: 25
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Provide one project-local provider-neutral MCP service

## Claim

### Prose Claim

One project-local provider-neutral MCP service **must** expose the complete active callable surface for Tools, Prompts and Workflows; ANECHOIC **must not** require one MCP server per capability. Programmatic calls return their results. Prompt calls return the selected prompt plus its invocation envelope for the main session. Workflow calls start or resume the applicable Workflow Run and return the next programmatic result, interactive Step invocation, Operator request, completion or failure state. Every exposed capability **must** remain usable headlessly without GRAPH_UI or an agent-host plugin. Agent-host plugins **may** package or connect to MCP but **must not** become the owner of provider-neutral MCP, Tool, Prompt or Workflow behavior.

Each MCP Tool call **must** be bound to the one trusted ProjectSelection of the service before native Tool dispatch. The Codex hook may carry a top-level project_root assertion. In single-Project mode it is optional for compatibility: omission uses the fixed bound Project, while a supplied value must match that Project's canonical host/container mapping and identity. In shared mode project_root is required and must select the already admitted ProjectSelection. A malformed or mismatched value is rejected before Tool execution and never switches the Project. The MCP boundary removes this hook field before passing native Tool arguments. MCP protocol operations such as initialize and tools/list are not treated as Tool-call argument envelopes; Workflow and Prompt wrappers keep their normal native dispatch.

Scope check: one project-local binds each service operation to one resolved Project frontier. A shared host may serve multiple explicit Project bindings through one service under CA-R-2008; this requirement does not impose a process-global one-Project restriction or a global current_project.

## Details

### Server lifecycle

For a Project exposing its generated Tool surface through MCP:

1. Bind one provider-neutral project-local service to one immutable ProjectSelection; a shared service may serve multiple explicit bindings.
2. Treat the Codex hook's top-level project_root only as a selection assertion. Omit it in single-Project mode to use the fixed selection; when supplied, validate canonical host path, container mapping, and identity. Require and validate it in shared mode. Do not wrap initialize/tools/list in this Tool-call envelope; Prompt and Workflow wrappers retain native dispatch.
3. Reject malformed, escaping, symlink-substituted, foreign, or mismatched assertions before native Tool dispatch, source or Journal effects, then remove the hook field from native Tool arguments.
4. Expose every eligible Tool without requiring GRAPH_UI or an agent-host plugin; no request may select another Project after binding. The complete callable surface remains headless, project-local, and provider-neutral.

Stop if an additional service becomes a competing authority, an assertion mismatches the bound selection, or a capability depends on App presentation. Do not introduce a process-global Project selector.
