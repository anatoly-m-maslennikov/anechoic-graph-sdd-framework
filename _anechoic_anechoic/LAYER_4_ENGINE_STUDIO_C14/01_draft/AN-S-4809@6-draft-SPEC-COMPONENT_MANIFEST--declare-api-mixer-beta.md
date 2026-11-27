---
atom_family: SPEC
atom_id: AN-S-4809
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 6
  updated_at: "2026-11-26T23:31:05Z"
---

## Summary

Declare API Mixer Beta

## Purpose

Serve the established Project Tool catalog in direct and shared HTTP modes.
MCP Patchbay supervises the separate API process. Keep the API stateless.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C91',
    name='API Mixer Beta',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []}, 'exports': {}},
 'io': {'server': {'project_api': {'transport': 'http',
                                   'socket': 'private Unix socket',
                                   'runner': 'managed_python',
                                   'module': 'API_MIXER_beta_C91.API_MIXER_beta_C91__shared',
                                   'process_role': 'api',
                                   'supervisor': 'C21',
                                   'arguments': 'existing single-Project '
                                                'API role startup '
                                                'arguments',
                                   'routes': ['GET /health',
                                              'GET /tools',
                                              'POST /tools']},
                   'shared_api': {'transport': 'http',
                                  'socket': 'private Unix socket',
                                  'runner': 'managed_python',
                                  'module': 'API_MIXER_beta_C91.shared_runtime',
                                  'supervisor': 'C21',
                                  'arguments': ['--socket',
                                                '<api-socket>',
                                                '--peer-owner-socket',
                                                '<owner-socket>',
                                                'optional --host-settings '
                                                '<settings>'],
                                  'routes': ['GET /health',
                                             'GET /tools',
                                             'POST /selection',
                                             'POST /tools']}},
        'client': {'shared_peer_owner': {'component': 'C68',
                                         'transport': 'newline-delimited '
                                                      'JSON over private '
                                                      'Unix socket',
                                         'operations': ['select',
                                                        'status',
                                                        'lease']},
                   'kernel': {'component': 'C71',
                              'transport': 'http',
                              'socket': 'private Unix socket',
                              'routes': ['GET /health',
                                         'GET /schema',
                                         'POST /database',
                                         'workspace and saved SQL '
                                         'operations',
                                         'POST /results/rebuild',
                                         'GET /ingestion/issues']},
                   'orchestrator': {'component': 'C68',
                                    'transport': 'http',
                                    'socket': 'private Unix socket',
                                    'routes': ['GET /health',
                                               'GET /jobs/worker-runs',
                                               'POST /jobs/build',
                                               'POST /jobs/abort',
                                               'POST /jobs/lifecycle', 'POST /jobs/atom-document']}}},
 'state': {'reads': ['admitted Project binding', 'peer readiness'],
           'writes': ['server-local readiness and bounded Project '
                      'identities for health']}}
```

## Component Contract

### Serve one admitted Project query through API Beta

#### Guarantee

Serve the admitted Project Tool capabilities through private HTTP, including
query, Workspace, View, saved SQL, projection, and Atom lifecycle operations.
MCP maps the catalog to its transport and forwards calls and results.
Enforce the selected Project's Tool blacklist.

Validate structured data with Pydantic. Send query, Workspace, and save
operations to the Project's Kernel. Send rebuild, abort, and lifecycle
operations to its Orchestrator. Preserve query IDs, typed results, file
descriptors, saved results, and reported outcomes. Apply AN-S-4803 to
HTTP outcomes.

Direct mode pins one Project binding. Shared mode requires an explicit
`project_root`. Use the C68 peer owner's selection and lease. Validate
the caller's admitted Project instance against the selection before
leasing. Validate the lease before use and the binding before returning
the result. Keep each request and its effects within the selected Project.

Kernel owns queries, accepted generations, and retained results.
Orchestrator owns refresh and Worker state. Keep API readiness
and health state local to its instance. Keep query and session state
out of the API.

### Serve a Console operation for its admitted Project

#### Guarantee

Run Console Views against the selected Project query projection.
For an Atom document, return its authored text, Current or exact revision,
and the admitted history and relations. Forward Draft updates and lifecycle
outcomes for the same Project. Distinguish a Realization Graph rebuild from
a Project database rebuild from source. Return readiness and Worker
statistics when Console status requests health.

```python trace
declare_trace_contract(action='serve_console_operation', cases={'failed': {'forbid_effect': ('C91.console',)},
 'succeeded': {'must_effect': (('C91.console',
                                'console_operation_returned'),)}})
```

### Read the selected Atom document

#### Guarantee

Validate the reference and the Project binding. Forward the read to C68.
Return the Current or exact revision and preserve its read failure.

```python trace
declare_trace_contract(action='dispatch_console_document', cases={'current': {'must_effect': (('C68.atom_document', 'returned', {'selector': 'current'}),)},
 'exact': {'must_effect': (('C68.atom_document', 'returned', {'selector': 'exact'}),)},
 'failed': {'forbid_effect': ('result',)}})
```

### Dispatch the requested Console rebuild

#### Guarantee

Forward the selected scope to C68. Return completion after C68 admits the
result. Report a refusal without claiming completion.

```python trace
declare_trace_contract(action='dispatch_console_rebuild', cases={'database_ready': {'must_effect': (('C68.build', 'admitted', {'scope': 'all'}),)},
 'failed': {'forbid_effect': ('result',)},
 'graph_ready': {'must_effect': (('C68.build',
                                  'admitted',
                                  {'scope': 'realization_graph'}),)}})
```

### Report Console runtime health

#### Guarantee

Sample the selected Project readiness. Include the indexing state and
known Worker and ingestion records.

```python trace
declare_trace_contract(action='report_console_runtime_health', cases={'healthy': {'must_effect': (('C91.console_status', 'reported', {'state': 'ready'}),)},
 'starting': {'must_effect': (('C91.console_status', 'reported', {'state': 'pending'}),)},
 'unavailable': {'must_effect': (('C91.console_status',
                                  'reported',
                                  {'state': 'unavailable'}),)},
 'unhealthy': {'must_effect': (('C91.console_status', 'reported', {'state': 'degraded'}),)}})
```
