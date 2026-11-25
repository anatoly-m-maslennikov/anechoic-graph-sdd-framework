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
  status: draft
  version: 21
  updated_at: '2026-11-25T15:11:49+00:00'
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
                'server': {
                    'manifest_runtime_start': {'outcomes': {
                        'succeeded': {'must_effect': [
                            ('C62.project_binding', 'admitted'),
                            ('C66.worker_run', 'completed'),
                            ('C62.model_attestation', 'verified'),
                            ('C62.fingerprint', 'verified'),
                            ('C62.artifacts', 'accepted'),
                            ('C62.structure', 'published'),
                        ]},
                        'failed': {'forbid_effect': ['C62.artifacts', 'C62.structure']},
                    }},
                    'manifest_runtime_refresh_structure': {'outcomes': {
                        'succeeded': {
                            'must_effect': [('C62.admitted_model', 'pinned'), ('C66.worker_run', 'completed'),
                                            ('C62.refresh_fingerprint', 'verified'),
                                            ('C62.structure_replacement', 'published_atomically')],
                            'forbid_effect': ['C62.model_replacement'],
                        },
                        'failed': {
                            'must_effect': [('C62.previous_structure', 'retained')],
                            'forbid_effect': ['C62.structure_replacement', 'C62.model_replacement'],
                        },
                    }},
                },
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
