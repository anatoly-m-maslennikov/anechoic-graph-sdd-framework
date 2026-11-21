---
atom_family: SPEC
atom_id: AN-S-1400
structure:
  container:
    component: C21
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Operate MCP headlessly without an App

## Claim

### Prose Claim

The project-local provider-neutral MCP service exposes an eligible Tool without App or plugin presentation, and binds every request to its admitted ProjectSelection before native dispatch.

## Details

| Test case | Acceptance criteria |
| --- | --- |
| Single-Project service without GRAPH_UI or an agent-host plugin | Tool remains discoverable/callable through fixed Project binding. |
| Single-Project hook omits project_root | Use fixed ProjectSelection and dispatch normally. |
| Single-Project hook supplies matching host/container root | Resolve one identity; native Tool receives only native arguments. |
| Single-Project hook supplies malformed/foreign/mismatched root | Reject before native Tool, Prompt, or Workflow execution, source, or Journal effect; do not switch Project. |
| Shared service omits project_root | Reject before dispatch because explicit binding is required. |
| Shared service supplies valid mapped root | Use selected ProjectSelection; consult no process-global Project. |
| tools/list boundary | Advertise optional project_root for single-Project and required for shared; native descriptors/schemas unchanged. |
| Prompt and Workflow calls | Return prompt invocation envelope and next resumable Workflow state through the same bound service. |

## Failure disposition

Reject deployment that depends on an App or transfers provider-neutral ownership to a plugin. Reject any request that changes the bound Project or passes the hook envelope as native Tool input.
