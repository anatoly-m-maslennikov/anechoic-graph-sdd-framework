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
  status: active
  version: 1
  updated_at: '2026-11-21T20:32:36.237351+00:00'
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
            'code_access': {
                'imports': ['C63', 'test_suite__pub.run_full_suite'],
                'exports': {
                    'PUBLIC_RELEASE__family_pub.run_public_release': {'family_pub': ['parent']},
                    'PUBLIC_RELEASE__family_pub.validate_draft': {'family_pub': ['parent']},
                },
            },
            'runtime_io': {
                'provides': {
                    'public_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_5_FRAMEWORK_DELIVERY/release.py',
                        'command': 'public',
                    },
                },
                'allows': [
                    {'component': 'C19', 'interface': 'test_suite'},
                    {'component': 'C63', 'interface': 'local_release'},
                ],
            },
            'shared_state': {
                'reads': ['Project Manifest', 'Project checkout', 'Public release content draft'],
                'writes': ['Project checkout', 'Public release pull request and branch'],
            },
        },
    ),
)
```
