---
atom_family: SPEC
atom_id: AN-S-2549
structure:
  container:
    component: C46
  tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:27:01.331088+00:00'
---
## Summary

Send Workbench browser operations through the Project API

## Claim scope

The Workbench browser transport.

## Claim

### Prose Claim

Send browser operations to the canonical `/anechoic/{project}/api/{operation}` endpoint for the selected Project. Route Workspace operations and Workspace-bound View saves through the shared `interface` operation. Return the response or surface the backend error.
