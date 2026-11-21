---
atom_family: SPEC
atom_id: AN-S-3044
container:
  component: C14
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-21T22:26:24.120851+00:00'
---

## Summary

Declare MCP

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C21',
        name='MCP',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code_access': {
                'imports': ['C15', 'C16', 'C45', 'C62'],
            },
            'runtime_io': {
                'provides': {
                    'shared_mcp_launcher': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py',
                    },
                    'shared_runtime_mcp': {
                        'transport': 'http',
                        'path': '/anechoic/mcp',
                        'protocol': 'mcp',
                    },
                },
            },
        },
    ),
)
```
