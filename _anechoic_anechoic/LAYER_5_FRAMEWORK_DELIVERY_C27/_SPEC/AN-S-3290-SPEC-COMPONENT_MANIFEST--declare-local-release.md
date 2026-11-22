---
atom_family: SPEC
atom_id: AN-S-3290
container:
  component: C27
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 7
  updated_at: '2026-11-22T11:23:40.206159+00:00'
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
            'code': {
                'imports': {'only': []},
                'exports': {
                    'RELEASE_VERSION__shared.run_local_release': {'private': ['parent']},
                    'RELEASE_VERSION__shared.build_image': {'private': ['parent']},
                },
            },
            'io': {
                'server': {
                    'test_packaged_image_identity': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_5_FRAMEWORK_DELIVERY.RELEASE_VERSION.RELEASE_VERSION__tests.packaged_image_fixture',
                        'arguments': ['<fixture-root>'],
                    },
                    'local_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_5_FRAMEWORK_DELIVERY/release.py',
                        'command': 'local',
                    },
                },
                'client': [{'component': 'C19', 'interface': 'test_suite'}],
            },
            'state': {
                'reads': ['Project Manifest literals', 'Checked-in registry', 'Active sources', 'Project checkout'],
                'writes': ['Project checkout', 'Local Framework installation', 'Project MCP runtime', 'Local Release receipts'],
            },
        },
    ),
)
```
