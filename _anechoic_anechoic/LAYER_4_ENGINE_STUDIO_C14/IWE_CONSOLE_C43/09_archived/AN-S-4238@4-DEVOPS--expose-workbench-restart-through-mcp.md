---
atom_family: SPEC
atom_id: AN-S-4238
container:
  component: C43
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Expose Workbench restart through MCP

## Claim scope

The selected Project's Workbench service operation in the existing MCP gateway.

## Claim

### Prose Claim

Expose the native MCP tool `workbench_restart({})`. It accepts no service name, shell command or container arguments. Close the old Workbench owner before starting its replacement. Return `{service: "workbench", status: "ready"}` only after fresh indexing succeeds. Return the shared explicit `workbench_unavailable` error when startup fails. Serialize restart with that Project's Workbench operations so an in-flight request cannot use a closed owner, including after caller cancellation. MCP and other services stay running. Old query-result IDs become unknown; saved-item IDs remain loadable. Restart itself writes no Business Journal event and adds no retry or rollback.

Health-page controls invoke this same native operation through the gateway. Do not add a second restart implementation, generic service registry, shell execution or Docker control.
