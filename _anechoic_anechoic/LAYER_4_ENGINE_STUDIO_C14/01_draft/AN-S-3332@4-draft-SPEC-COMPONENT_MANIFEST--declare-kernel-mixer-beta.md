---
atom_family: SPEC
atom_id: AN-S-3332
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T12:51:52+00:00'
---
## Summary

Declare Kernel Mixer Beta

## Purpose

Contain Beta's Database Server and the read-only Model and Structure Hosts
in one local Kernel process. The Backend starts and stops that process;
the Database Server owns its storage and serves the private API.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C67',
        name='Kernel Mixer Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {'server': {
                'database_api': {
                    'component': 'C71',
                    'transport': 'http',
                    'socket': 'private Unix socket',
                    'module': 'KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared',
                    'routes': {'health': 'GET /health', 'schema': 'GET /schema',
                               'ingestion_issues': 'GET /ingestion/issues',
                               'replace_ingestion_issues': 'PUT /ingestion/issues',
                               'query': 'POST /database', 'workspace': 'POST /workspace',
                               'rebuild_results': 'POST /results/rebuild',
                               'admit': 'PUT /generation', 'reuse': 'GET /generation/reuse',
                               'flow_events': 'POST /flow/events',
                               'admit_native': 'PUT /generation/native',
                               'admit_native_delta': 'PUT /generation/native-delta',
                               'model': 'GET /model', 'structure': 'GET /structure'},
                },
                'beta_artifact_read': {
                    'outcomes': {
                        'succeeded': {'must_effect': [('artifact_response', 'paired')]},
                        'foreign_instance': {'forbid_effect': ['artifact_response']},
                        'no_generation': {'forbid_effect': ['artifact_response']},
                    },
                },
            }},
            'state': {
                'reads': ['bound Project instance and accepted generation'],
                'writes': ['process-local Database Server connection and lock'],
            },
        },
    ),
)
```
