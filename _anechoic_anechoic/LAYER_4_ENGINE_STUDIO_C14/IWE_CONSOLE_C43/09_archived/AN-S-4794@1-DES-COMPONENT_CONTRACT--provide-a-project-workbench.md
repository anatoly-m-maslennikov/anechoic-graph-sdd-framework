---
atom_family: SPEC
atom_id: AN-S-4794
container:
  component: C43
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3046
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:01.655964+00:00"
---

## Summary

Provide a Project Workbench

## Guarantee

Provide a browser Workspace for an admitted Project and expose its Workbench
operations through the Project interface. A View holds SQL and its result;
Run and Check use the selected Project. Report failed operations to the caller.

The browser maintains local drafts and display preferences. The Backend owns
Project operation dispatch; the Kernel owns query execution and projection.
Saved items and transient results follow their respective owners' lifetimes.
Provide the Workbench MCP App resource and the static Realization Graph through
their respective Components.
