---
atom_family: SPEC
atom_id: AN-S-3326
container:
  component: C00
tier: 0
context:
  template: project_contract
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-22T11:34:35.965837+00:00'
relations:
  SERVES:
  - AN-S-1233
---
## Summary

MCP

## Inputs

The caller supplies a supported MCP operation and its required arguments.
For an operation on a shared runtime, the caller selects the repository.

## Guarantee

Return structured information, the effects of an authorized operation,
or an error that the caller can act on. Return query results inline or by
file reference. If saving fails after a query succeeds, return the query
result and identify the save failure.

Support multiple repositories in one runtime. Scope reads, writes,
results, Workspaces, and saved Views to the selected repository. Reject
missing, ambiguous, and mismatched selections when a request cannot be
bound to one repository.
