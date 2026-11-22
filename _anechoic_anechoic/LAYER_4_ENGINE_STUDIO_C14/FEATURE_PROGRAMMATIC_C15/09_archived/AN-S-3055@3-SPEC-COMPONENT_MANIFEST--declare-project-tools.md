---
atom_family: SPEC
atom_id: AN-S-3055
container:
  component: C15
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-22T04:30:12.094598+00:00"
---

## Summary

Declare PROJECT_TOOLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C19',
        name='PROJECT_TOOLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'exports': {
                    'test_suite__pub': 'public',
                    'test_suite__pub.run_full_suite': 'public',
                },
            },
            'io': {
                'server': {
                    'test_suite': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py',
                    },
                },
            },
        },
    ),
)
```
