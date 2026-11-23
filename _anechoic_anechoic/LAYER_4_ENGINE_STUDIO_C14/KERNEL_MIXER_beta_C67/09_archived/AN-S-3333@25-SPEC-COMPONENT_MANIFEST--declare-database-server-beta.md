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
  status: "archived"
  version: 25
  updated_at: "2026-11-23T00:32:58.404871+00:00"
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
        boundaries={'code': {'imports': {'only': ['CS5', 'CS6', 'ADAPTERS_C30__shared.attach_framework', 'ADAPTERS_C30__shared.migrate_project_database', 'ADAPTERS_C30__shared.append_sealed_events', 'DATABASE_SERVER_beta_C71__shared.create_app']},
                             'exports': {'DATABASE_SERVER_beta_C71__shared.create_app': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']}}},
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
                                                       'reuse': 'GET /generation/reuse',
                                                       'flow_events': 'POST /flow/events',
                                                       'admit_native': 'PUT /generation/native',
                                                       'admit_native_delta': 'PUT /generation/native-delta',
                                                       'model': 'GET /model',
                                                       'structure': 'GET /structure'},
                                            'artifact_read_fields': ['instance_id'],
                                            'artifact_generation_header': 'x-anechoic-generation',
                                            'query_fields': [['instance_id', 'sql'],
                                                             ['instance_id',
                                                              'sql',
                                                              'page_size'],
                                                             ['instance_id',
                                                              'query_id',
                                                              'offset',
                                                              'page_size']],
                                            'optional_paged_query_fields': ['grid', 'preview', 'result_delivery', 'result_format', 'save', 'name'],
                                            'rebuild_fields': ['instance_id', 'target'],
                                            'workspace_fields': ['instance_id', 'operation', 'arguments'],
                                            'query_history_operations': ['query_log_list', 'query_log_get'],
                                            'saved_query_operations': ['query_load', 'query_saved_list', 'view_save'],
                                            'optional_admit_fields': ['refresh_target', 'reuse', 'carrier_hashes'],
                                            'reuse_fields': ['inputs', 'graph_config', 'endpoints'],
                                            'carrier_hashes': 'Project-relative paths to SHA-256, complete for snapshots and present paths only for deltas',
                                            'admit_native_delta_max_paths': 1024,
                                            'admit_native_delta_fields': ['instance_id', 'base_generation',
                                                                          'paths', 'snapshot', 'snapshot_sha256'],
                                            'admit_native_graph_fields': ['graph', 'graph_sha256', 'optional reuse'],
                                            'optional_native_fields': ['carrier_hashes'],
                                            'admit_native_fields': ['instance_id', 'base_generation',
                                                                    'snapshot', 'snapshot_sha256'],
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
                              'disposable Project result files',
                              'Realization Graph rows in the accepted generation',
                              'durable Project Workspace and View documents',
                              'committed DuckDB Work Journal inbox records',
                              'Saved SQL snapshots in the admitted Project Journal',
                              'connection-local Journal projection for files mode',
                              'Project-scoped technical query history and its SQL view']}},
    ),
)
```
