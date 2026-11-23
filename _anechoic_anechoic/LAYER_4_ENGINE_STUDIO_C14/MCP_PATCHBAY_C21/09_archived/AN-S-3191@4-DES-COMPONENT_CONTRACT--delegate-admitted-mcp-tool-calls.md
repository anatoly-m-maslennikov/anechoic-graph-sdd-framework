---
atom_family: SPEC
atom_id: AN-S-3191
container:
  component: C21
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3044
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-23T00:35:11.078959+00:00"
---

## Summary

Delegate admitted MCP Tool calls

## Guarantee

For an admitted Project, expose the Tools in the Backend JSON catalog.
Preserve each Tool's name, description, and input schema. Forward the
Tool name, arguments, and request context to Backend and return its
result or failure through MCP.

Backend owns Tool eligibility, validation, and dispatch. MCP can read the
Project Manifest and runtime settings through declared interfaces for
Project binding and startup. The MCP bridge has zero production
cross-Component imports.

## References

AN-S-1381, AN-S-1391, AN-S-3044, and AN-T-2944.
