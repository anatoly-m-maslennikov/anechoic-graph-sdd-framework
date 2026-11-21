---
atom_family: TKT
atom_id: AN-T-2776
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-18T23:17:25.192748+00:00'
---
## Summary

Select the native Project Manifest at runtime

## Concern

Which carrier and settings should MCP and Workbench use to bind the native
Project during coexistence?

## Details

CA-R-3171 and the generated Project Manifest define Tier −1, a Project
container, and up to 20 settings. They leave the on-disk discovery method
and the minimum runtime identity fields open. The current project selector
requires legacy TOML and Scope Unit declarations.

Use a distinct native selection from one Active Project Manifest. Keep the
legacy selector available for Local Release. Confirm the Manifest carrier
lookup, the source of the Project name and prefix, and the lens of that
root structural Atom before building the migrated runtime adapter.

CA-P-3075 owns the migration and runtime check.
