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
  status: "archived"
  version: 2
  updated_at: '2026-11-24T19:35:54.327066+00:00'
relations:
  ANSWERS:
  - AN-S-4809@2
  IS_REFERENCE:
  - AN-S-1913@15
  - AN-S-4803@1
---

## Summary

Serve one admitted Project query through API Beta

## Guarantee

Serve the read-only Tool family through private HTTP. The catalog covers
`query_run`, `query_check`, `query_page`, and `query_schema`. MCP maps the
catalog to its transport and forwards calls and results. Enforce the
selected Project's Tool blacklist.

Validate structured data with Pydantic. Send the Project's schema or
query request to its Kernel. Preserve query IDs, typed results, file
descriptors, and reported outcomes. Reject query saves. Apply AN-S-4803
to HTTP outcomes.

Direct mode pins one Project binding. Shared mode requires an explicit
`project_root`. Use the C70 peer owner's selection and lease. Validate
the binding before use and before returning the result. Keep each
request and its effects within the selected Project.

Kernel owns queries, accepted generations, and retained results.
Orchestrator owns refresh and Worker state. Keep API readiness
and health state local to its instance. Keep query and session state
out of the API.
