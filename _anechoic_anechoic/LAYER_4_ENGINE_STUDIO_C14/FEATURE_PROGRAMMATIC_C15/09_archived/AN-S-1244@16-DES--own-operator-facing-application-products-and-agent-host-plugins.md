---
atom_family: SPEC
atom_id: AN-S-1244
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Own Operator-Facing Application Products and Agent-Host Plugins

# Summary

Own Operator-Facing Application Products and Agent-Host Plugins

## Scope

PROGRAMMATIC behavior governing APPS.

## Claim

APPS **must** own ANECHOIC application services, optional Operator-facing interfaces, Workflow orchestration, **and** agent-host plugin packages. A headless application service **must not** depend on its optional UI.

APPS **must** contain the unordered GRAPH_SERVER, GRAPH_UI, WORKFLOW_ORCHESTRATOR, MCP and AGENT_HOST_PLUGINS Scope Units. MCP and WORKFLOW_ORCHESTRATOR are peers: MCP supplies discovery and transport; WORKFLOW_ORCHESTRATOR owns Workflow execution and coordination. GRAPH_UI remains optional at runtime; GRAPH_SERVER supports headless use.

## Details
