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
  status: archived
  version: 2
  updated_at: '2026-11-21T21:49:45.763566+00:00'
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
                'imports': [],
                'exports': {
                    'RELEASE_VERSION__family_pub.run_local_release': {'family_pub': ['parent']},
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
                'reads': ['Project Manifest literals', 'Checked-in registry', 'Active sources', 'Project checkout'],
                'writes': ['Project checkout', 'Local Framework installation', 'Project MCP runtime', 'Local Release receipts'],
            },
        },
    ),
)
```
