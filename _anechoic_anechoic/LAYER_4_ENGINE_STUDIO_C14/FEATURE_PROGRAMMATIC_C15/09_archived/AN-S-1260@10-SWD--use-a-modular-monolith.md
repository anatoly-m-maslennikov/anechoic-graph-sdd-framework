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
  version: 10
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Use a modular monolith

## Claim

### Prose Claim

Implement the PROGRAMMATIC runtime as one modular application with shared queue and run state. Keep clear module boundaries aligned with Scope Unit responsibilities. Scope ownership does not require a one-to-one mapping to modules or deployments. Do not introduce separate services or internal network APIs merely to separate Scope Units.

## Details

### Scope

New or changed PROGRAMMATIC runtime implementation, including all descendant
Scope Units that contribute to that runtime.

Adapters, Single Actions, schedulers, Workflows, the Action Engine and MCP retain
distinct responsibilities within the shared runtime. Scope Units define
responsibility and ownership, not deployment boundaries.
