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
  version: 18
  updated_at: "2026-11-22T22:58:54.243694+00:00"
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
        boundaries={'code': {'imports': {'only': ['WORKBENCH_BACKEND_beta_C70__shared.open_warm_worker']},
                              'exports': {'WORKBENCH_BACKEND_beta_C70__shared.open_warm_worker': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKBENCH_BACKEND_beta_C70/WORKBENCH_BACKEND_beta_C70__tests']}}},
         'io': {'server': {'shared_workbench_api': {'transport': 'http',
                                                    'socket': 'private Unix socket',
                                                    'runner': 'managed_python',
                                                    'module': 'WORKBENCH_BACKEND_beta_C70.shared_runtime',
                                                    'arguments': ['--socket',
                                                                  '<socket>',
                                                                  '--host-settings',
                                                                  '<config>',
                                                                  'optional --peer-owner-socket <socket>'],
                                                    'routes': ['GET /health',
                                                               'GET /tools',
                                                               'POST /selection',
                                                               'POST /tools']},
                           'shared_peer_owner': {'transport': 'newline-delimited JSON over private Unix socket',
                                                 'runner': 'managed_python',
                                                 'module': 'WORKBENCH_BACKEND_beta_C70.shared_peer_owner',
                                                 'arguments': ['--socket', '<socket>', '--host-settings', '<config>'],
                                                 'operations': ['status', 'lease'],
                                                 'lease': 'admitted binding and start flag until release or disconnect'},
                           'workbench_api': {'transport': 'http',
                                             'socket': 'private Unix socket',
                                             'runner': 'managed_python',
                                             'module': 'WORKBENCH_BACKEND_beta_C70.runtime',
                                             'routes': ['GET /health',
                                                        'GET /tools',
                                                        'POST /tools',
                                                        'GET /jobs/worker-runs'],
                                             'process_roles': ['combined', 'peer-owner', 'api'],
                                             'admission': 'peer-owner marks initial admission on the private runtime path',
                                             'optional_arguments': ['--role', '<combined-peer-owner-or-api>', '--watch-code', '--workbench-storage', '<disk-or-memory>',
                                                                    '--project-name', '<admitted-name>',
                                                                    '--journal-storage', '<files-or-duckdb>',
                                                                    '--journal-relative', '<admitted-relative-path>',
                                                                    '--result-ttl-seconds', '<seconds>']}},
                'client': {'database': {'component': 'C71', 'transport': 'http',
                             'disk_argument': ['--database-path', '<bound-Project-file>'],
                             'schema': 'GET /schema',
                             'workspace': 'POST /workspace',
                             'query': 'POST /database',
                             'result_options': ['preview', 'result_delivery', 'result_format'],
                             'query_history_operations': ['query_log_list', 'query_log_get'],
                             'saved_query_operations': ['query_load', 'query_saved_list'],
                             'rebuild_results': 'POST /results/rebuild'},
                           'warm_worker': {'component': 'C69', 'interface': 'warm_ticket_delta',
                                           'lifetime': 'one per shared peer owner or standalone runtime'},
                           'jobs': {'component': 'C68', 'transport': 'http',
                                    'routes': ['GET /jobs/worker-runs', 'POST /jobs/build', 'POST /jobs/abort', 'POST /jobs/lifecycle']},
                           'project_admission': {'component': 'C53',
                                                 'interface': 'project_admission'}}},
         'state': {'reads': ['admitted Project binding', 'shared host settings'],
                   'writes': ['peer owner keeps bounded Project peer leases in memory',
                              'Backend keeps recent Project identities for health reporting']}},
    ),
)
```
