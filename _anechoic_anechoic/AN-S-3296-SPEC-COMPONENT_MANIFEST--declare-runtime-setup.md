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
  version: 5
  updated_at: '2026-11-22T11:23:40.206159+00:00'
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
                    'RUNTIME_SETUP__shared.select_settings': 'shared',
                    'RUNTIME_SETUP__shared.write_settings': 'shared',
                },
            },
            'io': {
                'server': {
                    'runtime_setup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'RUNTIME_SETUP/setup.py',
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
