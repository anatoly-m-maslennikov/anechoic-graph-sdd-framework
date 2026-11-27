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
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:28.111960+00:00"
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
                                               'POST /jobs/lifecycle']}}},
 'state': {'reads': ['admitted Project binding', 'peer readiness'],
           'writes': ['server-local readiness and bounded Project '
                      'identities for health']}}
```

## Component Contract

### Serve one admitted Project query through API Beta

#### Guarantee

Serve the established 33 Tool capabilities through private HTTP, including
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
