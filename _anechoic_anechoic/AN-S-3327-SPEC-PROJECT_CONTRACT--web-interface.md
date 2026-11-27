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
  version: 4
  updated_at: '2026-11-27T17:49:09.957980+00:00'
relations:
  SERVES:
  - AN-S-3037
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
