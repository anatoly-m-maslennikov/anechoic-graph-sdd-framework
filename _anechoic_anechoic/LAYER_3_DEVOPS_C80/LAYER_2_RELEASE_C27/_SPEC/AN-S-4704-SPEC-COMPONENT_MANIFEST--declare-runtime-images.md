---
atom_family: SPEC
atom_id: AN-S-4704
container:
  component: C27
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare Runtime Images

## Purpose

Build and run runtime images. Delegate shared container launch to the Engine shared MCP launcher and provide reusable Project-scoped container start for Local Release.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C81',
        name='Runtime Images',
        layer=1,
        lens_whitelist=['DevOps'],
        boundaries={
            'code': {
                'imports': {
                    'only': [
                        'C81', 'release_assets.LocalReleaseError', 'release_container.start_container',
                        'release_images', 'release_inputs', 'runtime_build',
                    ],
                },
            },
            'io': {
                'server': {
                    'runtime_images': {
                        'transport': 'cli', 'runner': 'uv',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                        'subcommands': {'build-image': 'C81', 'run-image': 'C81'},
                    },
                },
                'client': [{'component': 'C21', 'interface': 'shared_mcp_launcher'}],
            },
        },
    ),
)
```
