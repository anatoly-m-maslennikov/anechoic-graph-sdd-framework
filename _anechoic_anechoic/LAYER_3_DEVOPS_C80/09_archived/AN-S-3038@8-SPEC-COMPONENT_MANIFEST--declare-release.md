---
atom_family: SPEC
atom_id: AN-S-3038
container:
  component: C80
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 8
  updated_at: '2026-11-23T14:26:46.661274+00:00'
---

## Summary

Declare Release

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C27',
        name='Release',
        layer=2,
        lens_whitelist=['DevOps'],
        boundaries={
            'code': {
                'imports': {'only': ['C27', 'C81', 'C63', 'C64']},
                'exports': {
                    'LAYER_2_RELEASE_C27__shared': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_RELEASE_C27__tests']},
                },
            },
            'io': {
                'server': {
                    'release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                        'subcommands': {'local': 'C63', 'public': 'C64', 'build-image': 'C81', 'run-image': 'C81'},
                    },
                },
            },
        },
    ),
)
```
