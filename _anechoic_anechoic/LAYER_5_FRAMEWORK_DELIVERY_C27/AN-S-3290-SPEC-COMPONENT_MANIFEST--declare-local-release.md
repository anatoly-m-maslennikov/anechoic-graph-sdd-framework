---
atom_family: SPEC
atom_id: AN-S-3290
container:
  component: C27
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-21T20:32:36.227088+00:00'
---

## Summary

Declare Local Release

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C63',
        name='Local Release',
        layer=1,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code_access': {
                'imports': ['test_suite__pub.run_full_suite'],
                'exports': {
                    'RELEASE_VERSION__family_pub.run_local_release': {'family_pub': ['parent', 'C64']},
                },
            },
            'runtime_io': {
                'provides': {
                    'local_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_5_FRAMEWORK_DELIVERY/release.py',
                        'command': 'local',
                    },
                },
                'allows': [{'component': 'C19', 'interface': 'test_suite'}],
            },
            'shared_state': {
                'reads': ['Project Manifest', 'Project checkout'],
                'writes': ['Project checkout', 'Local Framework installation', 'Project MCP runtime'],
            },
        },
    ),
)
```
