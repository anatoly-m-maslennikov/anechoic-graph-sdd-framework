---
atom_family: SPEC
atom_id: AN-S-1400
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Operate MCP headlessly without an App

## Claim

### Prose Claim

The project-local provider-neutral MCP service exposes an eligible Tool without App or plugin presentation, and binds every request to its admitted ProjectSelection before native dispatch.

## Details

| Test case | Acceptance criteria |
| --- | --- |
| Single-Project service without GRAPH_UI or an agent-host plugin | The Tool remains discoverable and callable through the fixed Project binding. |
| Single-Project hook omits project_root | The service uses its fixed ProjectSelection and dispatches normally. |
| Single-Project hook supplies the matching host or container project_root | The host/container mapping resolves to the same Project identity and the Tool receives only its native arguments. |
| Single-Project hook supplies malformed, foreign or mismatched project_root | The request is rejected before native Tool, Prompt or Workflow execution, source effect or Journal effect; no Project switch occurs. |
| Shared service omits project_root | The request is rejected before dispatch because shared mode requires an explicit Project binding. |
| Shared service supplies a valid mapped project_root | The selected ProjectSelection is used and no process-global Project is consulted. |
| tools/list boundary advertisement | Single-Project discovery advertises optional project_root; shared discovery advertises required project_root; native Tool descriptors and schemas are unchanged. |
| Prompt and Workflow calls | The prompt returns its invocation envelope and the Workflow returns its next resumable state through the same bound service. |

## Failure disposition

Reject an MCP deployment that depends on an App or transfers provider-neutral ownership to a plugin. Reject a request that can change the bound Project or pass the hook envelope through as native Tool input.
