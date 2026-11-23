---
atom_family: SPEC
atom_id: AN-S-1948
container:
  component: C43
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:34:40 +0400
---

## Summary

Deliver query-visible audit tables

## Claim

### Prose Claim

Deliver these stable SQL tables through the shared Workbench backend and the existing `query_run` and `query_page` interfaces:

- `atom_content_issues`
- `atom_declared_carrier_issues`
- `atom_physical_carrier_issues`

Each table has only these columns: `reference` (nullable), `relative_path`, `filename`, `issue_category`, `property` (nullable), `observed` (nullable), `expected` (nullable), and `diagnostic`. HTTP and MCP must use the same backend and these exact names. Include the tables in the rebuildable schema only when their source declarations are valid. Do not call undeclared columns, add an Action, add background repair, add a second storage authority or change a source automatically.

