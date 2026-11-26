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
  status: draft
  version: 3
  updated_at: '2026-11-25T12:00:00Z'
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

## Claim

### Prose Claim

Load the selected bundle before returning its HTML. Report Unknown UI
resource when the URI is unknown or the Workbench build is unavailable.

### Formal Claim

```python trace
declare_trace_contract(
    action='codex_extension_read_resource',
    output='succeeded',
    must_effect=(
        ('C48.selected_bundle', 'loaded'),
        ('C48.resource_html', 'returned'),
    ),
    must_precede=(
        (('C48.selected_bundle', 'loaded'), ('C48.resource_html', 'returned')),
    ),
)
```

```python trace
declare_trace_contract(
    action='codex_extension_read_resource',
    output='failed',
    must_effect=(
        ('C48.resource_error', 'unknown_ui_resource'),
    ),
    forbid_effect=('C48.resource_html',),
)
```

The proof checks the logical error and response effects. Exact URI
selection, MIME and error wire values, listing, probe, and ping
remain in the Guarantee.

## References

AN-S-3058 and AN-T-2947.
