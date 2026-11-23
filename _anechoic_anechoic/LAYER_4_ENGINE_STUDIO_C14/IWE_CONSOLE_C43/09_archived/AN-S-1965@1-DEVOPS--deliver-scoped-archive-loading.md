---
atom_family: SPEC
atom_id: AN-S-1965
container:
  component: C43
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T01:43:22.100271+00:00'
---
## Summary

Deliver scoped Archive loading

## Claim scope

The shared Workbench Archive loading contract in HTTP and MCP.

## Claim

### Prose Claim

`workbench_archive_load` takes `scopes`, a nonempty array of `{scope_unit, role}` pairs. The Workbench web interface calls `POST /api/archive-load` beneath its existing Project route. Both adapters use the same selected Project owner and return `loaded_archive_scopes`, the complete array of pairs already loaded by that owner. Workbench status exposes the same coverage.

The load completes when selected `atoms` rows are published. Audit results can follow independently. Ordinary SQL reads the existing `atoms` table.