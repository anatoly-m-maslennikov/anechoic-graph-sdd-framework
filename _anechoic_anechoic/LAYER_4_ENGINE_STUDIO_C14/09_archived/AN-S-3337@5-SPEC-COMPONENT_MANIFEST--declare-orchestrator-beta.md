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
  version: 5
  updated_at: "2026-11-22T15:27:11.581454+00:00"
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
        boundaries={'code': {'imports': {'only': []}},
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
                                                  'optional --watch-code'],
                                    'routes': ['GET /health',
                                               'POST /jobs/build',
                                               'GET /jobs/worker-runs'],
                                    'build_request': ['instance_id', 'root', 'control_root', 'manifest_path',
                                                      'manifest_sha256', 'project_prefix']}},
                'client': {'snapshot_worker': {'component': 'C69', 'transport': 'cli'},
                           'database': {'component': 'C71',
                                        'transport': 'http',
                                        'route': 'PUT /generation'}}},
         'state': {'reads': ['pinned Project binding',
                             'Project source change events',
                             'code and dependency file events when the Graph is enabled'],
                   'writes': ['active build and latest Worker outcome in memory']}},
    ),
)
```
