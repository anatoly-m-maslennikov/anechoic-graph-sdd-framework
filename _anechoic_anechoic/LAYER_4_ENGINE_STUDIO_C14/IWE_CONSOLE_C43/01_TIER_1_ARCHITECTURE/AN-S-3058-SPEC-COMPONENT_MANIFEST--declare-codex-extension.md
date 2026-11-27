---
atom_family: SPEC
atom_id: AN-S-3058
container:
  component: C43
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 8
  updated_at: "2026-11-26T15:52:28.261716+00:00"
---

## Summary

Declare CODEX_EXTENSION

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C48',
    name='CODEX_EXTENSION',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['FEATURE_CODEX_EXTENSION__shared']},
          'exports': {'FEATURE_CODEX_EXTENSION__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_CODEX_EXTENSION/FEATURE_CODEX_EXTENSION__tests']},
                      'FEATURE_CODEX_EXTENSION__shared.call': None,
                      'FEATURE_CODEX_EXTENSION__shared.list_resources': None,
                      'FEATURE_CODEX_EXTENSION__shared.read_resource': None,
                      'FEATURE_CODEX_EXTENSION__shared.tools': None}},
 'state': {'reads': ['bundled compatibility probe HTML',
                     'bundled Workbench MCP App HTML'],
           'writes': []}}
```

## Component Contract

### Provide Workbench MCP App resources and a compatibility probe

#### Guarantee

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

#### References

AN-S-3058 and AN-T-2947.
