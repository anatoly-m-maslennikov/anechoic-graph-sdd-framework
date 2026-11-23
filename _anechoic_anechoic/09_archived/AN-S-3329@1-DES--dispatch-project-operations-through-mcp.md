---
atom_family: SPEC
atom_id: AN-S-3329
container:
  component: C00
tier: 3
context:
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3326
  CONTRIBUTES_TO:
  - AN-S-1855
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T11:00:54.983176+00:00'
---
## Summary

Dispatch Project operations through MCP

## Solution

Use the active Tool registry to publish supported Tool inputs and
outputs through MCP. Route Tool calls to the shared Workbench and
lifecycle services for the selected Project. Return the service
result and any operation diagnostics.

## References

AN-S-1242.
