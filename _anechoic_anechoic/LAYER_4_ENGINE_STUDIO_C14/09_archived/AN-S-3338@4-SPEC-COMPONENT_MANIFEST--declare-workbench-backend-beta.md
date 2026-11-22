---
atom_family: SPEC
atom_id: AN-S-3338
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-22T13:08:06.743354+00:00"
---
## Summary

Declare Workbench Backend Beta

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C70',
        name='Workbench Backend Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': {'only': []}},
         'io': {'server': {'shared_workbench_api': {'transport': 'http',
                                                    'socket': 'private Unix socket',
                                                    'runner': 'managed_python',
                                                    'module': 'WORKBENCH_BACKEND_beta_C70.shared_runtime',
                                                    'arguments': ['--socket',
                                                                  '<socket>',
                                                                  '--host-settings',
                                                                  '<config>'],
                                                    'routes': ['GET /health',
                                                               'GET /tools',
                                                               'POST /selection',
                                                               'POST /tools']},
                           'workbench_api': {'transport': 'http',
                                             'socket': 'private Unix socket',
                                             'runner': 'managed_python',
                                             'module': 'WORKBENCH_BACKEND_beta_C70.runtime',
                                             'routes': ['GET /health',
                                                        'GET /tools',
                                                        'POST /tools',
                                                        'GET /jobs/worker-runs']}},
                'client': {'database': {'component': 'C71', 'transport': 'http'},
                           'jobs': {'component': 'C68', 'transport': 'http'},
                           'project_admission': {'component': 'C53',
                                                 'interface': 'project_admission'}}},
         'state': {'reads': ['admitted Project binding', 'shared host settings'],
                   'writes': ['bounded Project peer leases and recent Project identities in '
                              'memory']}},
    ),
)
```
