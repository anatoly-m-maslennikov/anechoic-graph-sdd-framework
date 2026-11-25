---
atom_family: SPEC
atom_id: AN-S-3291
container:
  component: C27
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 7
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare Public Release

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C64',
        name='Public Release',
        layer=3,
        lens_whitelist=['DevOps'],
        boundaries={
            'code': {
                'imports': {'only': ['C64']},
            },
            'io': {
                'server': {
                    'public_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                        'command': 'public',
                    },
                },
                'client': [],
            },
            'state': {
                'reads': ['Git commits and completed Task and Epic Markdown', 'Public release content draft'],
                'writes': [],
            },
        },
    ),
)
```
