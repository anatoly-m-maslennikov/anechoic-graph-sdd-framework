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
  version: 1
  updated_at: 2026-11-05 05:49:16 +0400
---

## Summary

Expose Workbench restart through MCP

## Claim scope

The selected Project's Workbench service operation in the existing MCP gateway.

## Claim

Expose the native MCP tool `workbench_restart({})`. It accepts no service name, shell command or container arguments. Close the old Workbench owner before starting its replacement. Return `{service: "workbench", status: "ready"}` only after fresh indexing succeeds. Return the shared explicit `workbench_unavailable` error when startup fails. Serialize restart with that Project's Workbench operations so an in-flight request cannot use a closed owner, including after caller cancellation. MCP and other services stay running. Old query-result IDs become unknown; saved-item IDs remain loadable. Restart itself writes no Business Journal event and adds no retry or rollback.

This service operation is MCP-only. It does not add a web route, frontend control, generic service registry, shell execution or Docker control.
