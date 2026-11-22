---
atom_family: SPEC
atom_id: AN-S-2544
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 17
  updated_at: '2026-11-21T13:13:26.138497+00:00'
---
## Summary

Rebuild the Workbench schema from source Atoms.

## Claim scope

The native Workbench schema and its source tables.

## Claim

### Prose Claim

Build the query schema from the native Atom Header and Content projections and the loaded Model’s Relations. Expose the same dotted lowercase snake_case paths through SQL and MCP schema discovery.

Source refresh updates data under the loaded Model. Restart to apply Model changes. Record unreadable source files in the queryable source read issue table.