---
atom_family: SPEC
atom_id: AN-S-1971
container:
  component: C21
tier: 5
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---
## Summary

Expose Project operations through the shared HTTP API

## Claim

### Prose Claim

Expose Project HTTP operations at `/anechoic/{project}/api/{operation}` for any client. Keep `/anechoic/workbench/{project}` as the Workbench page. The existing Workbench operation URLs remain compatibility aliases to the same handlers.

Keep the existing operation names, request arguments and responses. Both URLs validate the Project name against the same selected Project and apply the same eligibility and dispatch rules. The Workbench frontend calls the shared Project API.
