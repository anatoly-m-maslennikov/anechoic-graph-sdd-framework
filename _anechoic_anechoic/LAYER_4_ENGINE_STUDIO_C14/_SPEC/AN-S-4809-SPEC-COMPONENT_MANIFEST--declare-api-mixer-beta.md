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
  status: "active"
  version: 4
  updated_at: "2026-11-24T23:05:55.115633+00:00"
---

## Summary

Declare API Mixer Beta

## Purpose

Serve the established Project Tool catalog in direct and shared HTTP modes.
MCP Patchbay supervises the separate API process. Keep the API stateless.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C91',
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
                        'module': 'API_MIXER_beta_C91.API_MIXER_beta_C91__shared',
                        'process_role': 'api',
                        'supervisor': 'C21',
                        'arguments': 'existing single-Project API role startup arguments',
                        'routes': ['GET /health', 'GET /tools', 'POST /tools'],
                    },
                    'shared_api': {
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'runner': 'managed_python',
                        'module': 'API_MIXER_beta_C91.shared_runtime',
                        'supervisor': 'C21',
                        'arguments': ['--socket', '<api-socket>', '--peer-owner-socket', '<owner-socket>',
                                      'optional --host-settings <settings>'],
                        'routes': ['GET /health', 'GET /tools', 'POST /selection', 'POST /tools'],
                    },
                },
                'client': {
                    'shared_peer_owner': {
                        'component': 'C68',
                        'transport': 'newline-delimited JSON over private Unix socket',
                        'operations': ['select', 'status', 'lease'],
                    },
                    'kernel': {
                        'component': 'C71',
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'routes': ['GET /health', 'GET /schema', 'POST /database',
                                   'workspace and saved SQL operations', 'POST /results/rebuild',
                                   'GET /ingestion/issues'],
                    },
                    'orchestrator': {
                        'component': 'C68',
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'routes': ['GET /health', 'GET /jobs/worker-runs', 'POST /jobs/build',
                                   'POST /jobs/abort', 'POST /jobs/lifecycle'],
                    },
                },
            },
            'state': {
                'reads': ['admitted Project binding', 'peer readiness'],
                'writes': ['server-local readiness and bounded Project identities for health'],
            },
        },
    ),
)
```
