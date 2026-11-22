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
  status: "active"
  version: 7
  updated_at: "2026-11-22T13:27:16.078197+00:00"
---

## Summary

Declare Runtime Setup

## Purpose

Install and configure the machine-local shared ANECHOIC runtime for selected Projects. Keep runtime settings under Runtime Setup ownership and initialize Project inputs only when requested.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C65',
        name='Runtime Setup',
        layer=6,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'RUNTIME_SETUP__shared.Settings': 'shared',
                    'RUNTIME_SETUP__shared.HOOK_SOURCE': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.MATCHER': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.install_codex': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.initialize_project': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.LAUNCHER': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.RELEASE': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.install': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.parse_arguments': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.select_settings': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                    'RUNTIME_SETUP__shared.write_settings': {'shared': ['LAYER_6_RUNTIME_SETUP/RUNTIME_SETUP__tests']},
                },
            },
            'io': {
                'server': {
                    'runtime_setup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_6_RUNTIME_SETUP/setup.py',
                        'command': 'install',
                    },
                },
                'client': [
                    {'component': 'C27', 'interface': 'release'},
                    {'component': 'C21', 'interface': 'shared_mcp_launcher'},
                ],
            },
            'state': {
                'writes': ['Machine-local runtime.toml', 'Explicitly initialized Project inputs', 'Codex user config when selected'],
            },
        },
    ),
)
```
