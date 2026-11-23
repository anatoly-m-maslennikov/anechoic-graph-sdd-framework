---
atom_family: SPEC
atom_id: AN-S-3847
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Define the APPS Scope Unit topology

## Claim

### Prose Claim

`APPS` **must** own the following immediate `unordered_unit` Scope Units: `WORKBENCH`, `GRAPH_UI`, **and** `AGENT_HOST_PLUGINS`.

- `WORKBENCH` owns the headless source indexer, rebuildable graph read model, **and** read-only query service derived from governed Atoms **and** Journals.
- `GRAPH_UI` owns the optional human interface over `WORKBENCH` **and** **must not** be required for headless Tool or MCP operation.
- `AGENT_HOST_PLUGINS` owns host-specific integration packages.

None of these applications, their databases, interfaces, or Projections becomes project authority.
