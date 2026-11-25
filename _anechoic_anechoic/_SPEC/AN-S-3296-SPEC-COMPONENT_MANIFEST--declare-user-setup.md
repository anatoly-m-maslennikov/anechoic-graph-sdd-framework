---
atom_family: SPEC
atom_id: AN-S-3296
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 9
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare User Setup

## Purpose

Install and configure the machine-local shared ANECHOIC runtime for selected Projects. Keep runtime settings under User Setup ownership and initialize Project inputs only when requested.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C65',
        name='User Setup',
        layer=5,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': ['C65']},
            },
            'io': {
                'server': {
                    'runtime_setup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_5_USER_SETUP_C65/setup.py',
                        'command': 'install',
                    },
                },
                'client': [
                    {'component': 'C27', 'interface': 'release'},
                ],
            },
            'state': {
                'writes': ['Machine-local runtime.toml', 'Explicitly initialized Project inputs', 'Codex user config when selected'],
            },
        },
    ),
)
```
