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
  status: draft
  version: 5
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
                    'build_and_run_runtime_images': {'outcomes': {
                        'image_result_reported': {'must_effect': [('C81.image_result', 'reported')]},
                    }},
                    'build_project_image': {'outcomes': {'succeeded': {
                        'must_effect': [('C81.image', 'built')],
                    }}},
                    'start_project_runtime': {'outcomes': {'succeeded': {
                        'must_effect': [('C81.project_container', 'launch_requested'), ('C81.mcp_endpoint', 'healthy')],
                    }}},
                    'apply_shared_runtime_launch': {'outcomes': {
                        'runtime_ready': {
                            'must_effect': [('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested'), ('C21', 'ready')],
                            'forbid_effect': ['shared_runtime_mcp_probe', 'shared_runtime_mcp'],
                        },
                        'mcp_verified': {
                            'must_effect': [('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested'), ('C21', 'ready'), ('shared_runtime_mcp_probe', 'requested'), ('shared_runtime_mcp', 'verified')],
                        },
                    }},
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
