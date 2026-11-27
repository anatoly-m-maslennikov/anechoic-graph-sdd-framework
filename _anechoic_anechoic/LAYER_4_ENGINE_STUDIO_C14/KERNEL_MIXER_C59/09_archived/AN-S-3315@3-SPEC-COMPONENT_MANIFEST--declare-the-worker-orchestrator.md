---
atom_family: SPEC
atom_id: AN-S-3315
container:
  component: C59
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:00.847121+00:00"
---
## Summary

Declare the Worker Orchestrator

## Purpose

Start short-lived Manifest Compiler workers and own their run records.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C66',
        name='Orchestrator',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {'ORCHESTRATOR_C66__shared.Orchestrator': None},
            },
            'io': {
                'server': {
                    'compiler_worker': {
                        'transport': 'in_process',
                        'entry': 'ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
                    },
                    'worker_runs': {
                        'transport': 'http',
                        'socket': 'private Kernel Unix socket',
                        'path': 'GET /jobs/worker-runs',
                        'query': {'instance_id': '<instance-id>'},
                    },
                },
                'client': [{'component': 'C50', 'interface': 'manifest_compile'}],
            },
            'state': {
                'reads': ['compiler exit status and process identity'],
                'writes': ['active Worker runs', 'latest terminal Worker run per kind'],
            },
        },
    ),
)
```
