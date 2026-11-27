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
  version: 7
  updated_at: '2026-11-27T17:00:30.949693+00:00'
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
                                  'routes': {'GET /health': 'health',
                                             'GET /tools': 'catalog',
                                             'POST /selection': 'selection',
                                             'POST /tools': 'invoke'}}},
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
                                               'POST /jobs/lifecycle']}}},
 'state': {'reads': ['admitted Project binding', 'peer readiness'],
           'writes': ['server-local readiness and bounded Project '
                      'identities for health']}}
```

## Component Contract

### Serve one admitted Project query through API Beta

#### Guarantee

Serve the installed Tool capabilities through private HTTP, including
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
the binding before use and before returning the result. Keep each
request and its effects within the selected Project.

Kernel owns queries, accepted generations, and retained results.
Orchestrator owns refresh and Worker state. Keep API readiness
and health state local to its instance. Keep query and session state
out of the API.

### Describe the shared Tool HTTP API at build time

#### Guarantee

Produce an OpenAPI 3.1 document for the shared `GET /tools` and
`POST /tools` routes. Derive its catalog and Tool arguments from the
same installed descriptors as the shared Backend catalog.

Use one invocation operation. Each request schema branch selects one
Tool name and its arguments. Include the shared HTTP Project, session,
and public URL fields where they are used. Source the document Version
from the packaged Framework Version.

The Backend applies Project selection and Tool admission at runtime.
The document describes the installed descriptors. Treat the live
catalog as the source for MCP discovery.

#### Verification

Validate the generated document as OpenAPI 3.1. Compare its Tool
catalog and argument schemas with the shared Backend. Verify the
success and typed failure envelopes against HTTP observations.

```python contract
declare_http_contract(
    interface='shared_api',
    action='listTools',
    endpoint='GET /tools',
    route_name='catalog',
    outcomes={'listed': (200, 'result')},
)
```

```python contract
declare_http_contract(
    interface='shared_api',
    action='invokeTool',
    endpoint='POST /tools',
    route_name='invoke',
    outcomes={'accepted': (200, 'result'),
 'refused': (200, 'typed_error'),
 'unavailable': (503, 'typed_error')},
)
```
