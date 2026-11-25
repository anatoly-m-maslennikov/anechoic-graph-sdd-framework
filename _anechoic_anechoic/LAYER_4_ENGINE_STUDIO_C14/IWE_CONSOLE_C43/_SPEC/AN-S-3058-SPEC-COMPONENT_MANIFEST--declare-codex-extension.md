---
atom_family: SPEC
atom_id: AN-S-3058
container:
  component: C43
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 6
  updated_at: "2026-11-24T21:35:30.943198+00:00"
---

## Summary

Declare CODEX_EXTENSION

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C48',
        name='CODEX_EXTENSION',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': ['FEATURE_CODEX_EXTENSION__shared']},
                'exports': {
                    'FEATURE_CODEX_EXTENSION__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_CODEX_EXTENSION/FEATURE_CODEX_EXTENSION__tests']},
                    'FEATURE_CODEX_EXTENSION__shared.call': None,
                    'FEATURE_CODEX_EXTENSION__shared.list_resources': None,
                    'FEATURE_CODEX_EXTENSION__shared.read_resource': None,
                    'FEATURE_CODEX_EXTENSION__shared.tools': None,
                },
            },
            'state': {
                'reads': ['bundled compatibility probe HTML', 'bundled Workbench MCP App HTML'],
                'writes': [],
            },
        },
    ),
)
```
