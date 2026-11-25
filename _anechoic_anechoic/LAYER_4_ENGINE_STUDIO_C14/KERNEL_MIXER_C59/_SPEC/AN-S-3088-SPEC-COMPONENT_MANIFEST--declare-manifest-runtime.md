---
atom_family: SPEC
atom_id: AN-S-3088
container:
  component: C59
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 20
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
                    'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                    'ORCHESTRATOR_C66__shared.Orchestrator',
                    'ADAPTERS_C30__shared.ARCHIVE_DIRECTORY',
                    'ADAPTERS_C30__shared.DRAFT_DIRECTORY',
                    'ADAPTERS_C30__shared.READY_DIRECTORY',
                    'ADAPTERS_C30__shared.owned_temporary_root',
                    'source_watcher__pub.SourceWatcher',
                ],
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
