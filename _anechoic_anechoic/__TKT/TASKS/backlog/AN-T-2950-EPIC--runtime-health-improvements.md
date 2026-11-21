---
atom_family: TKT
atom_id: AN-T-2950
structure:
  container:
    component: C21
  priority: 2
context:
  template: task
  label: Epic
state:
  status: "backlog"
  version: 1
  updated_at: "2026-11-21T14:34:56.590872+00:00"
---
## Summary

Runtime health improvements

## Objective

Make the runtime’s existing self-diagnostics available on the health page and through MCP.

## Work

- Reuse the health page’s diagnostics snapshot as the shared source.
- Expose the same readiness, availability, Project context and recent call observations through a read-only MCP tool with a structured JSON result.

## Acceptance

- The page and MCP report the same fields, status and safe error categories for the same snapshot.
- MCP can report degraded or unknown state when the gateway can still respond, including when Workbench is unavailable.
- The existing readiness probe keeps its response contract.