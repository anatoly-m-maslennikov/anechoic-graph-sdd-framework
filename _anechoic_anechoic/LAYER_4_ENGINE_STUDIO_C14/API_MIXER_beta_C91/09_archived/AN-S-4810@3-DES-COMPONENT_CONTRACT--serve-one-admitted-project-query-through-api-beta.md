---
atom_family: SPEC
atom_id: AN-S-4810
container:
  component: C91
tier: 0
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:01.697474+00:00"
relations:
  ANSWERS:
  - AN-S-4809@3
  IS_REFERENCE:
  - AN-S-1913@15
  - AN-S-4803@1
---

## Summary

Serve one admitted Project query through API Beta

## Guarantee

Serve the established 33 Tool capabilities through private HTTP, including
query, Workspace, View, saved SQL, projection, and Atom lifecycle operations.
MCP maps the catalog to its transport and forwards calls and results.
Enforce the selected Project's Tool blacklist.

Validate structured data with Pydantic. Send query, Workspace, and save
operations to the Project's Kernel. Send rebuild, abort, and lifecycle
operations to its Orchestrator. Preserve query IDs, typed results, file
descriptors, saved results, and reported outcomes. Apply AN-S-4803 to
HTTP outcomes.

Direct mode pins one Project binding. Shared mode requires an explicit
`project_root`. Use the C68 peer owner's selection and lease. Validate
the binding before use and before returning the result. Keep each
request and its effects within the selected Project.

Kernel owns queries, accepted generations, and retained results.
Orchestrator owns refresh and Worker state. Keep API readiness
and health state local to its instance. Keep query and session state
out of the API.
