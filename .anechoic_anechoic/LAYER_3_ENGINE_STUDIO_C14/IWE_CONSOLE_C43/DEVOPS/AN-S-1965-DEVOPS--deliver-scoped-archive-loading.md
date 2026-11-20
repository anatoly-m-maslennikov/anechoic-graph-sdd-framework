---
identity:
  atom_id: AN-S-1965
context:
  container:
    component: C43
  tier: 5
  lens: DevOps
state:
  status: active
  version: 2
  updated_at: '2026-11-12T16:59:34.762014+00:00'
---
## Summary

Deliver scoped Archive loading

## Claim scope

The shared Workbench Archive loading contract in HTTP and MCP.

## Claim

### Prose Claim

`workbench_archive_load` takes `scopes`, a nonempty array of `{scope_unit, role}` pairs. The Workbench web interface calls `POST /anechoic/{project}/api/archive-load`. The existing Workbench archive-load URL remains an alias to the same handler. Both adapters use the same selected Project owner and return `loaded_archive_scopes`, the complete array of pairs already loaded by that owner. Workbench status exposes the same coverage.

The load completes when selected `atoms` rows are published. Audit results can follow independently. Ordinary SQL reads the existing `atoms` table.
