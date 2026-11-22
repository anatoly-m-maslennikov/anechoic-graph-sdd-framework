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
  status: "active"
  version: 2
  updated_at: "2026-11-22T11:57:56.223650+00:00"
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
        boundaries={'code': {'imports': {'only': ['source_watcher__pub.SourceWatcher']}},
         'io': {'server': {'jobs': {'transport': 'http',
                                    'socket': 'private Unix socket',
                                    'runner': 'managed_python',
                                    'module': 'ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__pub',
                                    'arguments': ['--socket',
                                                  '<socket>',
                                                  '--instance-id',
                                                  '<instance-id>',
                                                  '--binding-file',
                                                  '<pinned-project-binding>',
                                                  '--database-socket',
                                                  '<kernel-socket>'],
                                    'routes': ['GET /health',
                                               'POST /jobs/build',
                                               'GET /jobs/worker-runs']}},
                'client': {'snapshot_worker': {'component': 'C69', 'transport': 'cli'},
                           'database': {'component': 'C71',
                                        'transport': 'http',
                                        'route': 'PUT /generation'}}},
         'state': {'reads': ['pinned Project binding', 'Project source change events'],
                   'writes': ['active build and latest Worker outcome in memory']}},
    ),
)
```
