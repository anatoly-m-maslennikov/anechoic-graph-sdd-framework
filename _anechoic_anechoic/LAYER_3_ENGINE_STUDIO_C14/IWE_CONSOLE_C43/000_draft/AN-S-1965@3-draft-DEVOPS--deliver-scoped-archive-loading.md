---
atom_family: SPEC
atom_id: AN-S-1965
structure:
  container:
    component: C43
  tier: 5
context:
  lens: DevOps
state:
  status: draft
  version: 3
  updated_at: '2026-11-14T07:53:03.724966+00:00'
---
## Summary

Deliver scoped Archive loading

## Claim

### Prose Claim

Load selected Archives through MCP `workbench_archive_load` and HTTP
`POST /anechoic/{project}/api/archive-load`.

## Details

- Accept a nonempty `scopes` array of `{scope_unit, role}` pairs.
- Use the selected Project's shared owner. Keep the legacy URL as an alias.
- Complete when selected `atoms` rows are queryable. Audits may follow.
- Return the owner's full `loaded_archive_scopes` list, also shown by status.
