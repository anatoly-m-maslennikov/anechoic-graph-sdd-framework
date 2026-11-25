---
atom_family: SPEC
atom_id: AN-S-3329
container:
  component: C00
tier: 1
context:
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3326
  CONTRIBUTES_TO:
  - AN-S-1855
state:
  status: active
  version: 2
  updated_at: '2026-11-22T22:22:00.577089+00:00'
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
