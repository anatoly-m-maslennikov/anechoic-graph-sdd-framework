---
atom_family: SPEC
atom_id: AN-S-4809
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T19:04:41.469060+00:00'
---

## Summary

Declare API Mixer Beta

## Purpose

Serve the first single-Project API Beta query slice from a separate process
supervised by MCP Patchbay.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C82',
        name='API Mixer Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'code': {'imports': {'only': []}, 'exports': {}},
            'io': {
                'server': {
                    'project_api': {
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'runner': 'managed_python',
                        'module': 'API_MIXER_beta_C82.API_MIXER_beta_C82__shared',
                        'process_role': 'api',
                        'supervisor': 'C21',
                        'arguments': 'existing single-Project API role startup arguments',
                        'routes': ['GET /health', 'GET /tools', 'POST /tools'],
                    },
                },
                'client': {
                    'kernel': {
                        'component': 'C71',
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'routes': ['GET /health', 'POST /database'],
                    },
                    'orchestrator': {
                        'component': 'C68',
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'routes': ['GET /health', 'GET /jobs/worker-runs'],
                    },
                },
            },
            'state': {
                'reads': ['admitted Project binding', 'peer readiness'],
                'writes': ['server-local admission readiness'],
            },
        },
    ),
)
```
