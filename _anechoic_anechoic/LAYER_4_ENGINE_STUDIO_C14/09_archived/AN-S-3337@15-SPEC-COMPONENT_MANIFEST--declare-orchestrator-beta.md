---
atom_family: SPEC
atom_id: AN-S-3337
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 15
  updated_at: "2026-11-22T21:50:58.950196+00:00"
---
## Summary

Declare Orchestrator Beta

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C68',
        name='Orchestrator Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': {'only': ['ORCHESTRATOR_beta_C68__shared']},
                              'exports': {'ORCHESTRATOR_beta_C68__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']}}},
         'io': {'server': {'jobs': {'transport': 'http',
                                    'socket': 'private Unix socket',
                                    'runner': 'managed_python',
                                    'module': 'ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared',
                                    'arguments': ['--socket',
                                                  '<socket>',
                                                  '--instance-id',
                                                  '<instance-id>',
                                                  '--binding-file',
                                                  '<pinned-project-binding>',
                                                  '--database-socket',
                                                  '<kernel-socket>',
                                                  'optional --watch-code',
                                                  'optional paired --worker-socket and --worker-load-seconds'],
                                    'routes': ['GET /health',
                                               'POST /jobs/build',
                                               'POST /jobs/lifecycle',
                                               'GET /jobs/worker-runs'],
                                    'build_request': ['instance_id', 'root', 'control_root', 'manifest_path',
                                                      'manifest_sha256', 'project_prefix'],
                                    'optional_build_field': 'refresh_target',
                                    'worker_mode': ['warm', 'cold'],
                                    'build_timings': ['worker_seconds', 'admission_seconds'],
                                    'optional_delta_field': 'delta_path_count',
                                    'lifecycle_request': 'build binding plus name and arguments',
                                    'lifecycle_result': ['lifecycle', 'write_state', 'projection']}},
                'client': {'snapshot_worker': {'component': 'C69', 'transport': 'cli'},
                           'warm_ticket_delta': {'component': 'C69', 'interface': 'warm_ticket_delta'},
                           'lifecycle_worker': {'component': 'C69', 'interface': 'task_lifecycle'},
                           'database': {'component': 'C71',
                                        'transport': 'http',
                                        'routes': ['GET /generation/reuse', 'GET /structure', 'PUT /generation', 'PUT /generation/native',
                                                   'PUT /generation/native-delta', 'POST /flow/events']}}},
         'state': {'reads': ['pinned Project binding',
                             'Project source change events',
                             'code and dependency file events when the Graph is enabled'],
                   'writes': ['active build, lifecycle request, latest Worker outcome and admitted input proof in memory']}},
    ),
)
```
