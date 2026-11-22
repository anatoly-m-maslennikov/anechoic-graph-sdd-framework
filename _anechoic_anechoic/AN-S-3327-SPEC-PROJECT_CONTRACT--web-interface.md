---
atom_family: SPEC
atom_id: AN-S-3327
container:
  component: C00
tier: 0
context:
  template: project_contract
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T11:00:54.983176+00:00'
relations:
  ADVANCES:
  - AN-S-1233
---
## Summary

Web Interface

## Inputs

The Operator opens a repository Workspace and supplies a query or
requests a supported action.

## Guarantee

Show query results, including results of queries over the Project graph.
Keep the Workspace and saved Views available for reopening. Show the
result of an action or why it failed. Show when the data is unavailable
or still updating.
