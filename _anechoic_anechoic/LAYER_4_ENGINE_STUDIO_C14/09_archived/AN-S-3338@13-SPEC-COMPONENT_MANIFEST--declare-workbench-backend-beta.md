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
  version: 13
  updated_at: "2026-11-22T17:11:54.690024+00:00"
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
                                                        'GET /jobs/worker-runs'],
                                             'optional_arguments': ['--watch-code', '--workbench-storage', '<disk-or-memory>',
                                                                    '--project-name', '<admitted-name>',
                                                                    '--journal-storage', '<files-or-duckdb>',
                                                                    '--journal-relative', '<admitted-relative-path>',
                                                                    '--result-ttl-seconds', '<seconds>']}},
                'client': {'database': {'component': 'C71', 'transport': 'http',
                             'disk_argument': ['--database-path', '<bound-Project-file>'],
                             'schema': 'GET /schema',
                             'workspace': 'POST /workspace',
                             'query': 'POST /database',
                             'result_options': ['result_delivery', 'result_format'],
                             'query_history_operations': ['query_log_list', 'query_log_get'],
                             'saved_query_operations': ['query_load', 'query_saved_list'],
                             'rebuild_results': 'POST /results/rebuild'},
                           'jobs': {'component': 'C68', 'transport': 'http',
                                    'routes': ['GET /jobs/worker-runs', 'POST /jobs/build', 'POST /jobs/lifecycle']},
                           'project_admission': {'component': 'C53',
                                                 'interface': 'project_admission'}}},
         'state': {'reads': ['admitted Project binding', 'shared host settings'],
                   'writes': ['bounded Project peer leases and recent Project identities in '
                              'memory']}},
    ),
)
```
