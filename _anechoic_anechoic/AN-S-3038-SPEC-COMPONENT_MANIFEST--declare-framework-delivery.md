---
atom_family: SPEC
atom_id: AN-S-3038
container:
  component: C00
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-21T20:39:26.276803+00:00'
---

## Summary

Declare Framework Delivery

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C27',
        name='Framework Delivery',
        layer=5,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'runtime_io': {
                'provides': {
                    'release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_5_FRAMEWORK_DELIVERY/release.py',
                        'subcommands': {'local': 'C63', 'public': 'C64'},
                    },
                },
            },
        },
    ),
)
```
