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
  status: archived
  version: 15
  updated_at: '2026-11-22T10:54:04.216780+00:00'
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
                    'ORCHESTRATOR_C66__shared.Orchestrator',
                    'native_carrier_placement__pub.ARCHIVE_DIRECTORY',
                    'native_carrier_placement__pub.DRAFT_DIRECTORY',
                    'native_carrier_placement__pub.READY_DIRECTORY',
                    'project_temporary__pub.owned_temporary_root',
                    'source_watcher__pub.SourceWatcher',
                ],
                'exports': {
                    'MANIFEST_RUNTIME_C62__shared.run_manifest_runtime': {
                        'private': ['C59'],
                    },
                },
            },
            'io': {
                'client': [
                    {'component': 'C66', 'interface': 'compiler_worker'},
                ],
            },
            'state': {
                'reads': ['pinned Project Manifest and compiler output'],
                'writes': ['admitted Model and Structure generation'],
            },
        },
    ),
)
```
