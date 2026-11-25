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
  status: archived
  version: 8
  updated_at: '2026-11-23T13:44:08.728884+00:00'
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
                'exports': {
                    'RUNTIME_SETUP__shared.main': {'private': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.Settings': 'shared',
                    'RUNTIME_SETUP__shared.HOOK_SOURCE': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.MATCHER': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.install_codex': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.initialize_project': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.LAUNCHER': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.RELEASE': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.install': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.parse_arguments': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.select_settings': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.write_settings': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                },
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
