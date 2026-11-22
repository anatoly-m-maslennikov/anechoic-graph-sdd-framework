---
atom_family: SPEC
atom_id: AN-S-3333
container:
  component: C67
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 14
  updated_at: "2026-11-22T16:08:34.632398+00:00"
---
## Summary

Declare Database Server Beta

## Purpose

Own the accepted Project generation, Workspaces, and query results.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C71',
        name='Database Server Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': {'only': ['CS5', 'CS6']}},
         'io': {'server': {'database_api': {'transport': 'http',
                                            'socket': 'private Unix socket',
                                            'arguments': ['--socket',
                                                          '<socket>',
                                                          '--instance-id',
                                                          '<instance-id>',
                                                          '--manifest-sha256',
                                                          '<manifest-sha256>'],
                                            'optional_arguments': ['--database-path', '<guarded-file>',
                                                                   '--project-root', '<admitted-root>',
                                                                   '--result-ttl-seconds', '<seconds>',
                                                                   '--journal-storage', '<files-or-duckdb>',
                                                                   '--journal-relative', '<admitted-relative-path>'],
                                            'routes': {'health': 'GET /health',
                                                       'schema': 'GET /schema',
                                                       'query': 'POST /database',
                                                       'workspace': 'POST /workspace',
                                                       'rebuild_results': 'POST /results/rebuild',
                                                       'admit': 'PUT /generation',
                                                       'model': 'GET /model',
                                                       'structure': 'GET /structure'},
                                            'query_fields': [['instance_id', 'sql'],
                                                             ['instance_id',
                                                              'sql',
                                                              'page_size'],
                                                             ['instance_id',
                                                              'query_id',
                                                              'offset',
                                                              'page_size']],
                                            'optional_query_field': 'grid',
                                            'rebuild_fields': ['instance_id', 'target'],
                                            'workspace_fields': ['instance_id', 'operation', 'arguments'],
                                            'query_history_operations': ['query_log_list', 'query_log_get'],
                                            'saved_query_operations': ['query_load', 'query_saved_list'],
                                            'optional_admit_field': 'refresh_target',
                                            'admit_fields': ['instance_id',
                                                             'snapshot',
                                                             'receipt',
                                                             'model',
                                                             'structure',
                                                             'graph'],
                                            'runner': 'managed_python',
                                            'module': 'KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared',
                                            'receipt_digests': ['snapshot_sha256', 'graph_sha256']}}},
         'state': {'reads': ['attested Project generation', 'bound disk generation on restart',
                              'sealed files in the admitted Project Journal directory',
                              'previously accepted Saved SQL in Journal and legacy cache carriers'],
                   'writes': ['accepted Project rows and paired artifacts in the database',
                              'bounded paged results in Kernel memory',
                              'Realization Graph rows in the accepted generation',
                              'durable Project Workspace and View documents',
                              'committed DuckDB Work Journal inbox records',
                              'connection-local Journal projection for files mode',
                              'Project-scoped technical query history and its SQL view']}},
    ),
)
```
