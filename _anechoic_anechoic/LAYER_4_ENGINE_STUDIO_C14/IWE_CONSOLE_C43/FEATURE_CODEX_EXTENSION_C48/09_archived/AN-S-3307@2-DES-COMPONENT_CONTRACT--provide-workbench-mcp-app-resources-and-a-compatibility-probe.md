---
atom_family: SPEC
atom_id: AN-S-3307
container:
  component: C48
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3058
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:01.378761+00:00"
---
## Summary

Provide Workbench MCP App resources and a compatibility probe

## Guarantee

List the Workbench and compatibility probe resources as
`text/html;profile=mcp-app`. Return the corresponding HTML for
`ui://anechoic/workbench.html` or
`ui://anechoic/workbench-compatibility-v2.html`.

Return MCP error `-32002` with `Unknown UI resource` for an unknown URI
or an unavailable Workbench build.

Expose the read-only `workbench_ui_probe` and `workbench_ui_ping` Tools
through the shared entry Module. The probe identifies its compatibility
resource and returns `ANECHOIC MCP App resource loaded`. The ping returns
`Tool bridge passed`. Refuse unsupported Tool names.

## References

AN-S-3058 and AN-T-2947.
