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
  status: draft
  version: 35
  updated_at: "2026-11-27T04:49:51+00:00"
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
{'code': {'imports': {'only': ['ADAPTERS_C30__shared.status_domains',
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
          'exports': {'DATABASE_SERVER_beta_C71__shared.open_database': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__tests']},
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
                     'accepted Structure and Component Seed projections',
                     'durable View SQL and cursor position',
                     'sealed files in the admitted Project Journal '
                     'directory',
                     'previously accepted Saved SQL in Journal and legacy '
                     'cache carriers'],
           'writes': ['accepted Project rows and paired artifacts in the '
                      'database',
                      'Component and Component Seed query projections',
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

Admit the Model, Structure, native revisions and relations, and enabled Realization Graph
in one transaction for the bound Project. Keep the prior generation on
failed admission. Serve its exact artifact bytes and one read-only SQL
SELECT per request, with no external access and at most 1,000 rows.
Validate Atom Status values against the admitted Model. Return those
domains with the generation's reuse proof.

Keep a 16 MiB result budget in Kernel. Charge serialized result and
SQL bytes with a 4 KiB minimum for each result. Limit each serialized
result to 1 MiB. Refuse a new result or refresh
that would exceed capacity. Do not evict young or pinned results.
Pages keep their result across a generation update. Open Views pin results.
Unpinned results expire after the configured startup lifetime of 3,600
seconds by default. View result IDs and rows are transient.

When Workbench selects disk storage, retain the accepted generation in a
private database bound to the Project instance and Manifest digest. Offer
the compatible persisted checkpoint when that binding reopens. Commit
the input proof, carrier inventory and content hashes, and Archive
pending state with the accepted generation.

Confirm the named base before reusing the projection or accepting
Incremental Startup changes. Update affected rows and their checkpoints
together. Remove checkpoints for paths that are absent, including the
previous paths of moves. Expose the current proof to Orchestrator.
Expose DuckPGQ queries for admitted imports
and Package and Component test relationships.

Keep each Workspace bound to its Project and session. Preserve View IDs
and edits across Kernel restarts independently of query storage. Refuse
stale View revisions and keep at least one View in each Workspace.

Retain View SQL and cursor position in the Workspace. For View Check, Run,
and Save, recognize a trailing View display directive outside SQL strings,
comments, and parentheses. Check and Run use the SELECT without that
directive. Save validates the SELECT without the directive and retains the
authored SQL intact.

Expose the accepted Component hierarchy and Component Seed owners, purposes,
and Manifest refs for SQL. Replace the Seed projection with the accepted
Structure in the same transaction. On reopening an older bound database,
restore its Seed projection from the retained Structure.

For DuckDB Work Journal storage, admit staged records into the Project's
existing Journal table. Remove an inbox record after its commit.
Refuse conflicting bytes for an accepted record ID.

Filter, sort, and group retained inline results before paging. On an
explicit result refresh, issue replacement IDs and update any View pins
in the same locked operation. For a projection rebuild, commit the new
generation and its result refresh together. Keep the prior generation
and result IDs if capture fails.

For file Journal storage, read the admitted Project-relative Journal
directory into a connection-local `work_journal` projection before SQL.
Keep the prior rows if a carrier cannot be validated.

Record query and View Run attempts through one ordered background writer
per Project owner. Retain their seven technical fields for 48 hours in
hourly UTC files. Expose the same retained attempts through read-only
list, get, and `query_log` SQL. Check creates no attempt. A log failure
leaves the Run response intact. Drain the writer on orderly shutdown.

Return public schema fields and available distinct Status values from the
same accepted generation. Omit hints outside the supported bound.
Schema reads create no technical query attempt.

Own Saved SQL for the admitted Project. Store a successful Query or View
Run with a save request as a Bookmark. Save View snapshots one valid
read-only SELECT from a bound View or explicit SQL text without running it.
Use a canonical UUIDv7 and append under the Project Journal's fixed
`workbench-saved-items` author. Use the selected file or DuckDB storage.
Return the ID after the write. A failed save preserves a successful Run
and its query ID and returns a partial outcome.

Load saved SQL by its admitted Project ID. List bounded metadata without
SQL bodies. Read compatible historical files and accepted DuckDB records
across Journal storage changes. Saved reads do not alter their carriers.

Deliver cached results inline or as disposable files under the admitted
Project. Export the whole accepted Run or the requested Page or View
Fetch as JSON matrix, CSV, or TOON. Preserve positional values and
column names. Return a partial outcome with the existing query ID when
an export fails. Keep the result available for later reads.

Apply a Run preview cap before materializing the result. Apply a Page
or View Fetch preview only to the delivered page. Preserve the Run
preview cap when refreshing the retained result.

Publish admitted Code Access findings with the Realization Graph. Keep
declared owner bypasses visible. Omit the graph tables when disabled.

Publish `code_units` and `code_unit_calls` in the same generation.
Expose Module membership and calls through DuckPGQ. Retain the source
Module on propagated effects.

Serve structural cycles, Package coupling, and antipattern evidence
through `import_cycles`, `package_coupling`, and `antipattern_findings`.

Mark Archive pending until background reconciliation succeeds. During
Incremental Startup, prior checkpoint Archive rows may remain visible
with that marker. On cold startup, expose no Archive rows before
admission.

Admit Archive additions, edits, moves, and deletions with their relations
and carrier hashes against the latest live generation in one transaction.
Preserve Current and Draft rows and the Realization Graph. Clear the
pending marker only when Archive admission succeeds.

Accept a native-only refresh against the named current generation.
Validate the native snapshot against the admitted Model. Replace Atom
and native relation rows in one transaction. Retain Model, Structure,
and Realization Graph rows when the request contains only a native
snapshot. When the request also supplies a Realization Graph and its
digest, validate it against the admitted Structure and replace it
in the same transaction. Retain the exact Model and Structure.
Refuse a stale generation and retain the prior state on failure.

A native carrier delta names the current generation and up to 1,024 affected paths.
Publish the changed Atom rows and Model-defined relations together in one
transaction, including their graph rows and Current Lens membership.
Retain the accepted Model, Structure, and Realization Graph. Request
reconciliation when the delta cannot preserve relation ownership.

Derive Component flows from observed events. Expose their causal
links and shared-action candidates in SQL. Admit each bound trace atomically. Preserve the
event stream across generation rebuilds and disk reopen.

#### References

AN-S-3333, AN-S-2242, AN-S-1356, AN-T-2958, and AN-T-2976.

### Admit Console Structure rows

#### Guarantee

Publish Components and Component Seeds from the same accepted Structure.
A rejected admission leaves the preceding rows available.

```python trace
declare_trace_contract(action='admit_structure_projection', cases={
    'succeeded': {'must_effect': (('C71.structure_projection', 'committed'),)},
    'failed': {'forbid_effect': ('C71.structure_projection',)},
})
```

### Interpret View SQL

Check, Run, and Save recognize a trailing display directive at the top level
of SQL. Graph and Imports accept an optional `VERTICAL` or `HORIZONTAL`.
Allow comments between directive words and after the directive. Save
validates the SELECT and retains the original View SQL.

```python trace
declare_trace_contract(action='save_view_sql', cases={
    'succeeded': {
        'must_effect': (('C71.view_select', 'validated'), ('C71.saved_view', 'saved')),
        'same_values': ((('view_requested', 'authored_sql'), ('view_saved', 'authored_sql')),),
    },
    'failed': {'forbid_effect': ('C71.saved_view',)},
})
```

```python trace
declare_trace_contract(action='check_view_sql', cases={
    'succeeded': {'must_effect': (('C71.view_select', 'validated'), ('C71.check_result', 'ready'))},
    'failed': {'forbid_effect': ('C71.check_result',)},
})
```

```python trace
declare_trace_contract(action='run_view_sql', cases={
    'succeeded': {'must_effect': (('C71.view_select', 'validated'), ('C71.view_result', 'ready'))},
    'failed': {'forbid_effect': ('C71.view_result',)},
})
```

### Admit a Graph-only rebuild

#### Guarantee

Require the named live generation and unchanged non-Graph inputs.
An explicit forced rebuild may keep the same Graph input digest.
Replace the Graph atomically and preserve Atom, Model, and Structure rows.

```python trace
declare_trace_contract(action='admit_console_graph', cases={
    'published': {
        'must_effect': (('C71.graph', 'admitted'),),
        'forbid_effect': ('C71.atoms', 'C71.model', 'C71.structure'),
    },
    'refused': {'forbid_effect': ('C71.graph', 'C71.atoms', 'C71.model', 'C71.structure')},
})
```
