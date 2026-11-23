---
atom_family: SPEC
atom_id: AN-S-4408
container:
  component: C20
tier: 2
context:
  lens: DevOps
state:
  status: archived
  version: 20
  updated_at: 2026-11-10 08:25:53 +0400
---

## Summary

Deliver the Requirement Projection browser locally

## Claim

### Prose Claim

Deliver the optional GRAPH_UI Requirement Projection browser as exactly one project-local, non-authoritative `_projection/mrt_atoms.html` under the selected Project’s declared authority root file with embedded JavaScript and presentation assets. Serve this generated asset through the selected Workbench listener, on the same origin as its query API. Back its live reads with the declared Workbench query contract and current indexed Atom Content, without a separate server, file-origin API access or a general source-file HTTP service.

Create no sibling web assets. This delivery is not required for headless Workbench, Tool or MCP operation and does not publish, host or distribute the MRT outside the Project. Deleting the generated file changes no governed Atom, Journal or other Projection.
