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
  status: draft
  version: 5
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
            'code': {'exports': {'ORCHESTRATOR_C66__shared.Orchestrator': None}, 'imports': {'only': []}},
            'io': {
                'server': {
                    'compiler_worker': {
                        'transport': 'in_process',
                        'entry': 'ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
                    },
                    'manifest_compiler_worker_run': {
                        'outcomes': {
                            'failed': {'must_effect': [('C66', 'failed')]},
                            'completed': {'must_effect': [
                                ('C66.worker_process', 'started'), ('C66.worker_process', 'reaped'),
                                ('C66.worker_run', 'completed'),
                            ]},
                            'timed_out': {'must_effect': [
                                ('C66.worker_process', 'started'), ('C66.worker_process', 'killed'),
                                ('C66.worker_process', 'reaped'), ('C66.worker_run', 'timed_out'),
                            ]},
                        },
                    },
                    'manifest_compiler_worker_status': {
                        'outcomes': {
                            'succeeded': {
                                'must_effect': [('C66.active_runs', 'returned'),
                                                ('C66.latest_terminal_runs', 'returned')],
                                'forbid_effect': ['C66.worker_process', 'C66.worker_run'],
                            },
                        },
                    },
                    'worker_runs': {
                        'transport': 'http',
                        'socket': 'private Kernel Unix socket',
                        'routes': {'GET /jobs/worker-runs': 'worker_runs'},
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
