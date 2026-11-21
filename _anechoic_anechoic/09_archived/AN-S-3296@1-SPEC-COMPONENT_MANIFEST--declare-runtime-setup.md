---
atom_family: SPEC
atom_id: AN-S-3296
container:
  component: C00
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T00:00:00Z'
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
            'code_access': {'imports': []},
            'runtime_io': {
                'provides': {
                    'runtime_setup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'RUNTIME_SETUP/setup.py',
                        'command': 'install',
                    },
                },
                'allows': [
                    {'component': 'C27', 'interface': 'release'},
                    {'component': 'C21', 'interface': 'shared_mcp_launcher'},
                    {'component': 'C21', 'interface': 'shared_runtime_mcp'},
                ],
            },
            'shared_state': {
                'writes': ['Machine-local runtime.toml', 'Explicitly initialized Project inputs', 'Codex user config when selected'],
            },
        },
    ),
)
```
