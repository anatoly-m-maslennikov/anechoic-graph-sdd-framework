---
atom_family: SPEC
atom_id: AN-S-1383
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Provide one project-local provider-neutral MCP service

# Provide one project-local provider-neutral MCP service

One project-local provider-neutral MCP service **must** expose the complete active callable surface for Tools, Prompts, **and** Workflows; ANECHOIC **must not** require one MCP server per capability. Programmatic calls return their results. Prompt calls return the selected prompt plus its invocation envelope for the main session. Workflow calls start **or** resume the applicable Workflow Run and return the next programmatic result, interactive Step invocation, Operator request, completion, **or** failure state. Every exposed capability **must** remain usable headlessly without `GRAPH_UI` **or** an agent-host plugin. Agent-host plugins **may** package **or** connect **to** MCP but **must not** become the owner of provider-neutral MCP, Tool, Prompt, **or** Workflow behavior.

Scope check: “one project-local” binds each service operation to one resolved
Project frontier. The shared host may serve multiple explicit Project bindings
through one service under CA-R-2008; this requirement does not impose a
process-global one-Project restriction or a global `current_project`.
