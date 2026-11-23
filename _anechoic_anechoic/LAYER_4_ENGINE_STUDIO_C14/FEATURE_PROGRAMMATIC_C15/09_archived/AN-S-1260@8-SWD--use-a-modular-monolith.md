---
atom_family: SPEC
atom_id: AN-S-1260
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 8
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Use a modular monolith

# Summary

Use a modular monolith

## Scope

New or changed PROGRAMMATIC runtime implementation, including all descendant
Scope Units that contribute to that runtime.

## Claim

Implement the PROGRAMMATIC runtime as one modular application with shared queue
and run state. Keep clear module boundaries aligned with Scope Unit
responsibilities. Do not introduce separate services or internal network APIs
merely to separate Scope Units.

## Details

Adapters, Single Actions, schedulers, Workflows, the Action Engine and MCP retain
distinct responsibilities within the shared runtime. Scope Units define
responsibility and ownership, not deployment boundaries.
