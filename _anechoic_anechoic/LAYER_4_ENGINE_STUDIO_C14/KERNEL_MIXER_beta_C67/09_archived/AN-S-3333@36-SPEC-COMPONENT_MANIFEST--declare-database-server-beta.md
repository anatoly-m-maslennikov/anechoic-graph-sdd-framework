---
atom_family: SPEC
atom_id: AN-S-3333
container:
  component: C67
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 36
  updated_at: "2026-11-27T15:10:44.706424+00:00"
---
## Summary

Declare Database Server Beta

## Purpose

Own the accepted Project generation, Workspaces, and query results.

Publish the admitted Model diagnostics and Project Structure for SQL.
Cap full-generation request bodies at 128 MiB. Bound DuckDB spill
when using disk-backed storage.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C71',
    name='Database Server Beta',
    lens_whitelist=['DES', 'SPEC', 'SWD/DBT'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['accepted_model.initialize',
                               'accepted_model.managed',
                               'accepted_model.prepare',
                               'accepted_model.publish',
                               'archive_generation',
                               'database_lifespan',
                               'generation_batch',
                               'model_entity_properties.primary_entity_properties',
                               'model_entity_tree.model_tree_rows',
                               'carrier_checkpoint',
                               'persistence',
                               'carrier_checkpoint.read_checkpoint',
                               'table_names.main_objects',
                               'ADAPTERS_C30__shared.status_domains',
                               'ADAPTERS_C30__shared.NODE_LINK_PREFIX',
                               'model_generation__pub._validate_binding_descriptor',
                               'CS5',
                               'CS6',
                               'ADAPTERS_C30__shared.attach_framework',
                               'ADAPTERS_C30__shared.console_state_path',
                               'ADAPTERS_C30__shared.migrate_project_database',
                               'ADAPTERS_C30__shared.append_sealed_events',
                               'ADAPTERS_C30__shared.canonical_model_address',
                               'ADAPTERS_C30__shared.model_class_target',
                               'DATABASE_SERVER_beta_C71__shared.create_app',
                               'DATABASE_SERVER_beta_C71__shared.result_ttl',
                               'DATABASE_SERVER_beta_C71__shared.open_database']},
          'exports': {'accepted_model.initialize': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'accepted_model.managed': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'accepted_model.prepare': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'accepted_model.publish': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'archive_generation': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'database_lifespan': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'generation_batch': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'model_entity_properties.primary_entity_properties': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'model_entity_tree.model_tree_rows': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'carrier_checkpoint': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'persistence': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'carrier_checkpoint.read_checkpoint': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'table_names.main_objects': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'DATABASE_SERVER_beta_C71__shared.connect': {'shared': ['C45']},
                      'DATABASE_SERVER_beta_C71__shared.open_database': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'DATABASE_SERVER_beta_C71__shared.create_app': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
                      'DATABASE_SERVER_beta_C71__shared.result_ttl': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']}}},
 'io': {'server': {'database_api': {'transport': 'http',
                                    'socket': 'private Unix socket',
                                    'arguments': ['--socket',
                                                  '<socket>',
                                                  '--instance-id',
                                                  '<instance-id>',
                                                  '--manifest-sha256',
                                                  '<manifest-sha256>'],
                                    'optional_arguments': ['--database-path',
                                                           '<guarded-file>',
                                                           '--project-root',
                                                           '<admitted-root>',
                                                           '--result-ttl-seconds',
                                                           '<seconds>',
                                                           '--journal-storage',
                                                           '<files-or-duckdb>',
                                                           '--journal-relative',
                                                           '<admitted-relative-path>'],
                                    'routes': {'health': 'GET /health',
                                               'schema': 'GET /schema',
                                               'ingestion_issues': 'GET '
                                                                   '/ingestion/issues',
                                               'replace_ingestion_issues': 'PUT '
                                                                           '/ingestion/issues',
                                               'query': 'POST /database',
                                               'workspace': 'POST '
                                                            '/workspace',
                                               'rebuild_results': 'POST '
                                                                  '/results/rebuild',
                                               'admit': 'PUT /generation',
                                               'reuse': 'GET '
                                                        '/generation/reuse',
                                               'flow_events': 'POST '
                                                              '/flow/events',
                                               'admit_native': 'PUT '
                                                               '/generation/native',
                                               'admit_native_delta': 'PUT '
                                                                     '/generation/native-delta',
                                               'model': 'GET /model',
                                               'structure': 'GET '
                                                            '/structure'},
                                    'artifact_read_fields': ['instance_id'],
                                    'ingestion_issue_read_fields': ['instance_id'],
                                    'ingestion_issue_replace_fields': ['instance_id',
                                                                       'source',
                                                                       'issues'],
                                    'artifact_generation_header': 'x-anechoic-generation',
                                    'query_fields': [['instance_id',
                                                      'sql'],
                                                     ['instance_id',
                                                      'sql',
                                                      'page_size'],
                                                     ['instance_id',
                                                      'query_id',
                                                      'offset',
                                                      'page_size']],
                                    'optional_paged_query_fields': ['grid',
                                                                    'preview',
                                                                    'result_delivery',
                                                                    'result_format',
                                                                    'save',
                                                                    'name'],
                                    'rebuild_fields': ['instance_id',
                                                       'target'],
                                    'workspace_fields': ['instance_id',
                                                         'operation',
                                                         'arguments'],
                                    'query_history_operations': ['query_log_list',
                                                                 'query_log_get'],
                                    'saved_query_operations': ['query_load',
                                                               'query_saved_list',
                                                               'view_save'],
                                    'optional_admit_fields': ['refresh_target',
                                                              'reuse',
                                                              'carrier_hashes'],
                                    'reuse_fields': ['inputs',
                                                     'graph_config',
                                                     'endpoints'],
                                    'carrier_hashes': 'Project-relative '
                                                      'paths to SHA-256, '
                                                      'complete for '
                                                      'snapshots and '
                                                      'present paths only '
                                                      'for deltas',
                                    'admit_native_delta_max_paths': 1024,
                                    'admit_native_delta_fields': ['instance_id',
                                                                  'base_generation',
                                                                  'paths',
                                                                  'snapshot',
                                                                  'snapshot_sha256'],
                                    'admit_native_graph_fields': ['graph',
                                                                  'graph_sha256',
                                                                  'optional '
                                                                  'reuse'],
                                    'optional_native_fields': ['carrier_hashes'],
                                    'admit_native_fields': ['instance_id',
                                                            'base_generation',
                                                            'snapshot',
                                                            'snapshot_sha256'],
                                    'admit_fields': ['instance_id',
                                                     'snapshot',
                                                     'receipt',
                                                     'model',
                                                     'structure',
                                                     'graph'],
                                    'runner': 'managed_python',
                                    'module': 'KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared',
                                    'receipt_digests': ['snapshot_sha256',
                                                        'graph_sha256']}}},
 'state': {'reads': ['attested Project generation',
                     'bound disk generation on restart',
                     'sealed files in the admitted Project Journal '
                     'directory',
                     'previously accepted Saved SQL in Journal and legacy '
                     'cache carriers'],
           'writes': ['accepted Project rows and paired artifacts in the '
                      'database',
                      'bounded paged results in Kernel memory',
                      'disposable Project result files',
                      'Realization Graph rows in the accepted generation',
                      'durable Project Workspace and View documents',
                      'committed DuckDB Work Journal inbox records',
                      'Saved SQL snapshots in the admitted Project '
                      'Journal',
                      'connection-local Journal projection for files mode',
                      'Project-scoped technical query history and its SQL '
                      'view']}}
```

## Component Contract

### Serve read-only SQL for the Beta Project snapshot

#### Guarantee

Bind Kernel to one Project. Admit Model, Structure, native revisions
and relations, and the enabled Graph atomically. Preserve the previous
generation on failure. Serve exact artifacts and one read-only SELECT
per request with no external access and at most 1,000 rows. Validate
Atom Status against the admitted Model and include its domains in reuse
proof.

On disk, bind the private database to the Project instance and Manifest
digest. Offer a compatible checkpoint on reopen. Commit the input proof,
carrier inventory and hashes, and Archive state with the generation.
Confirm the named base before reusing it or applying startup deltas.
Update rows and checkpoints together, removing absent and old move paths.
Expose the proof to Orchestrator.

Keep a 16 MiB result budget, including serialized SQL and result bytes,
with a 4 KiB minimum per result and a 1 MiB serialized result cap. Refuse
excess admission or refresh. Preserve result IDs across generation updates.
Pin open View results and retain young results. Unpinned results expire
after the startup-configured lifetime, by default 3,600 seconds. Results
and their IDs are transient.

Bind Workspaces to Project and session. Retain View IDs and edits across
restart independently of query storage. Refuse stale revisions. Keep at
least one View per Workspace.

Commit staged DuckDB Journal records to the existing Project table before
removing the inbox record. Refuse conflicting bytes for a record ID. For
file Journals, project the admitted Project-relative carriers into the
connection-local `work_journal` table before SQL. Keep prior rows if
validation fails.

Filter, sort, and group inline results before paging. On explicit refresh,
replace IDs and update View pins in one locked operation. A projection
rebuild commits refreshed results with the new generation. Failed capture
preserves prior generation and result IDs.

Log query and View Run attempts through one ordered background writer per
Project owner. Retain seven technical fields in hourly UTC files for 48
hours. Expose the same entries through read-only list, get, and
`query_log`. Check and schema reads create no attempt. Logging failure
preserves the Run response. Drain the writer on orderly shutdown. Serve
bounded schema fields and distinct Status values from one admitted
generation.

Save successful Query or View Runs requested as Bookmarks. Save View
snapshots one valid read-only SELECT from the bound View or explicit SQL
without running it.
Use canonical UUIDv7 and the fixed `workbench-saved-items` Journal author
in the selected file or DuckDB storage. Return ID after write. Failed save
returns partial with any successful Run and its query ID. Load by admitted
Project and ID. List bounded metadata without SQL. Read compatible
historical files and DuckDB records across storage changes without
mutating carriers.

Return cached rows inline or disposable Project files. Export full Run
or requested Page or View Fetch as JSON matrix, CSV, or TOON, preserving
positions and column names. On export failure return partial with the
query ID and retain the result. Apply Run preview before materialization
and retain it at refresh. Apply Page and Fetch previews only to delivery.

Publish Code Access findings, declared bypasses, `code_units`,
`code_unit_calls`, `import_cycles`, `package_coupling`, and
`antipattern_findings` with the Graph. Omit Graph tables when disabled.
Expose imports, Package and Component tests, Module membership and calls
through DuckPGQ. Preserve source Module on propagated effects.

Mark Archive pending until successful background admission. Apply
AN-S-3389 to prior Archive visibility and cold startup. Admit Archive
changes, relations, and hashes atomically against the latest live base,
preserving Current, Draft, and Graph.

For a native refresh, validate the snapshot under the admitted Model.
Replace Atom and native relation rows atomically against the current
generation. Preserve Model, Structure, and Graph, except that a supplied
Graph and digest can replace Graph rows after Structure validation.
Refuse stale bases and preserve prior state on failure. A native delta
names up to 1,024 paths and the current generation. Admit affected Atom
rows, relations, Graph rows, and Current Lens membership together.
Preserve accepted Model, Structure, and Graph authority. Request
reconciliation when relation ownership cannot be preserved.

Derive Component flows from observed events, exposing causal links and
shared-action candidates in SQL. Admit each bound trace atomically and
retain it across rebuilds and disk reopen.

#### References

AN-S-3333, AN-S-2242, AN-S-1356, AN-T-2958, and AN-T-2976.
