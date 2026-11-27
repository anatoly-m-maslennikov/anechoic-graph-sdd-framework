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
  version: 22
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Own Operator-Facing Application Products and Agent-Host Plugins

## Scope

PROGRAMMATIC behavior governing APPS.

## Claim


### Prose Claim
APPS **must** own ANECHOIC application services, optional Operator-facing interfaces, Workflow orchestration, **and** agent-host plugin packages. A headless application service **must not** depend on its optional UI.

MCP supplies discovery and transport; Workflow orchestration owns Workflow execution and coordination. WORKBENCH supports headless use.

