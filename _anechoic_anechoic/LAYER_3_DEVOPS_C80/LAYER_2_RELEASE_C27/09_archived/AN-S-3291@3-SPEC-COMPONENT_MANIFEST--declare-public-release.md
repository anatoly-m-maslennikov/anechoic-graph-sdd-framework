---
atom_family: SPEC
atom_id: AN-S-3291
container:
  component: C27
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-21T22:51:12.819403+00:00'
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
        layer=2,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'PUBLIC_RELEASE__shared.run_public_release': {'private': ['parent']},
                },
            },
            'io': {
                'server': {
                    'public_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_5_FRAMEWORK_DELIVERY/release.py',
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
