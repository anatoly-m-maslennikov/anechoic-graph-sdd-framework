---
atom_family: SPEC
atom_id: AN-S-3088
container:
  component: C59
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 11
  updated_at: "2026-11-22T06:49:24.489867+00:00"
---

## Summary

Declare Manifest Runtime

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C62',
        name='Manifest Runtime',
        lens_whitelist=['SPEC'],
        boundaries={
            'code': {
                'imports': [
                    'model_generation__pub.open_admitted_model',
                    'model_generation__pub.verify_model',
                    'native_carrier_placement__pub.ARCHIVE_DIRECTORY',
                    'native_carrier_placement__pub.DRAFT_DIRECTORY',
                    'native_carrier_placement__pub.READY_DIRECTORY',
                    'project_temporary__pub.owned_temporary_root',
                    'source_watcher__pub.SourceWatcher',
                ],
                'exports': {
                    'MANIFEST_RUNTIME_C62__shared.run_manifest_runtime': {
                        'private': ['LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND'],
                    },
                },
            },
            'io': {
                'client': [
                    {'component': 'C50', 'interface': 'manifest_compile'},
                    {'component': 'C50', 'interface': 'image_model_compile'},
                ],
            },
            'state': 'local',
        },
    ),
)
```
