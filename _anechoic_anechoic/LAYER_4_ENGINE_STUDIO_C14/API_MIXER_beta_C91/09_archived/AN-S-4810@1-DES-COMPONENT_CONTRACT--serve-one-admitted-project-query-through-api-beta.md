---
atom_family: SPEC
atom_id: AN-S-4810
container:
  component: C82
tier: 0
context:
  template: component_contract
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T19:04:41.469060+00:00'
relations:
  ANSWERS:
  - AN-S-4809@1
  IS_REFERENCE:
  - AN-S-1913@15
  - AN-S-4803@1
---

## Summary

Serve one admitted Project query through API Beta

## Guarantee

Serve one admitted Project through the private HTTP socket. The initial
Tool catalog contains `query_run` when the Project permits it. MCP maps the
catalog to its transport and forwards Tool requests and results.

Validate the Project binding, Tool request, and query result with Pydantic.
Forward read-only SQL and its paging and delivery options to the exact
Project Kernel. Return its query ID and typed inline page or file result.
Reject a request to save the query. Apply AN-S-4803 to HTTP outcomes.

Kernel owns query execution, accepted generation, and retained results.
Orchestrator owns Project refresh and Worker state. Keep the API binding
and readiness scoped to the server instance. Use private HTTP sockets for
peer calls. Keep Project and query state out of process globals.
