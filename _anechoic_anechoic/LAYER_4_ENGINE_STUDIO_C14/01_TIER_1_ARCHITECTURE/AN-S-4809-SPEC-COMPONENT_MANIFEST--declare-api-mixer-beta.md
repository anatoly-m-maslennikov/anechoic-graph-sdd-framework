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
  version: 11
  updated_at: "2026-11-28T15:00:42+00:00"
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
{'code': {'imports': {'only': [
                                 'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.API',
                                 'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.ENGINE',
                                 'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.OWNER',
                                 'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.write_manifest',
                                 'CORE.CORE__shared.ALIASES',
                                 'CORE.CORE__shared.FLOWS',
                                 'CORE.CORE__shared.Invocation',
                                 'CORE.CORE__shared.JobsHealth',
                                 'CORE.CORE__shared.KernelHealth',
                                 'CORE.CORE__shared.Owner',
                                 'CORE.CORE__shared.Page',
                                 'CORE.CORE__shared.PageRequest',
                                 'CORE.CORE__shared.PeerHealth',
                                 'CORE.CORE__shared.Query',
                                 'CORE.CORE__shared.Readiness',
                                 'CORE.CORE__shared.SelectionRequest',
                                 'CORE.CORE__shared.Sql',
                                 'CORE.CORE__shared.SqlResult',
                                 'CORE.CORE__shared.StrictModel',
                                 'CORE.CORE__shared.TABLES',
                                 'CORE.CORE__shared.TOOL_REST_PATH',
                                 'CORE.CORE__shared.ToolRequest',
                                 'CORE.CORE__shared.WorkerBinding',
                                 'CORE.CORE__shared.WorkerRuns',
                                 'CORE.CORE__shared.atom_document',
                                 'CORE.CORE__shared.failure',
                                 'CORE.CORE__shared.fault',
                                 'CORE.CORE__shared.owner_fault',
                                 'CORE.CORE__shared.peer',
                                 'CORE.CORE__shared.public_tool',
                                 'CORE.CORE__shared.read_schema',
                                 'CORE.CORE__shared.tool_unavailable',
                                 'OPERATIONS.OPERATIONS__shared.lifecycle',
                                 'OPERATIONS.OPERATIONS__shared.projection',
                                 'OPERATIONS.OPERATIONS__shared.saved_sql',
                                 'OPERATIONS.OPERATIONS__shared.view_tools',
                                 'OPERATIONS.OPERATIONS__shared.workspace',
'FEATURE_MCP.transport_support.transport_support__shared.Invocation',
                                 'FEATURE_MCP.transport_support.paths.paths__shared.TOOL_REST_PATH',
                                 'FEATURE_IWE_CONSOLE_BACKEND__shared.public_tool',
                                 'API_MIXER_beta_C91__shared.export_openapi']},
          'exports': {
                      'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.API': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests']},
                      'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.ENGINE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests/runtime_cases']},
                      'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.OWNER': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests/runtime_cases']},
                      'API_MIXER_beta_C91__tests.archive_cases.archive_cases__shared.write_manifest': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests/runtime_cases']},
                      'CORE.CORE__shared.ALIASES': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.FLOWS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.Invocation': {'private': ['C91']},
                      'CORE.CORE__shared.JobsHealth': {'private': ['C91']},
                      'CORE.CORE__shared.KernelHealth': {'private': ['C91']},
                      'CORE.CORE__shared.Owner': {'private': ['C91']},
                      'CORE.CORE__shared.Page': {'private': ['C91', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.PageRequest': {'private': ['C91']},
                      'CORE.CORE__shared.PeerHealth': {'private': ['C91']},
                      'CORE.CORE__shared.Query': {'private': ['C91']},
                      'CORE.CORE__shared.Readiness': {'private': ['C91', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.SelectionRequest': {'private': ['C91']},
                      'CORE.CORE__shared.Sql': {'private': ['C91']},
                      'CORE.CORE__shared.SqlResult': {'private': ['C91']},
                      'CORE.CORE__shared.StrictModel': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.TABLES': {'private': ['LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.TOOL_REST_PATH': {'private': ['C91']},
                      'CORE.CORE__shared.ToolRequest': {'private': ['C91']},
                      'CORE.CORE__shared.WorkerBinding': {'private': ['C91']},
                      'CORE.CORE__shared.WorkerRuns': {'private': ['C91', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.atom_document': {'private': ['C91']},
                      'CORE.CORE__shared.failure': {'private': ['C91', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.fault': {'private': ['C91']},
                      'CORE.CORE__shared.owner_fault': {'private': ['C91']},
                      'CORE.CORE__shared.peer': {'private': ['C91', 'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/OPERATIONS']},
                      'CORE.CORE__shared.public_tool': {'private': ['C91']},
                      'CORE.CORE__shared.read_schema': {'private': ['C91']},
                      'CORE.CORE__shared.tool_unavailable': {'private': ['C91']},
                      'OPERATIONS.OPERATIONS__shared.lifecycle': {'private': ['C91']},
                      'OPERATIONS.OPERATIONS__shared.projection': {'private': ['C91']},
                      'OPERATIONS.OPERATIONS__shared.saved_sql': {'private': ['C91']},
                      'OPERATIONS.OPERATIONS__shared.view_tools': {'private': ['C91']},
                      'OPERATIONS.OPERATIONS__shared.workspace': {'private': ['C91']},
'API_MIXER_beta_C91__shared.descriptors': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/static']},
                      'API_MIXER_beta_C91__shared.export_openapi': {'private': [
                      'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/static',
                      'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests/runtime_cases',
                      'LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91/API_MIXER_beta_C91__tests/api_cases/static']}}},
 'io': {'server': {'current_openapi_export': {
                           'transport': 'cli',
                           'runner': 'managed_python',
                           'module': 'API_MIXER_beta_C91.openapi',
                           'arguments': ['--registry', '<packaged-tool-registry>',
                                         '--version-file', '<framework-version-file>']},
                   'project_api': {'transport': 'http',
                                   'socket': 'private Unix socket',
                                   'runner': 'managed_python',
                                   'module': 'API_MIXER_beta_C91.API_MIXER_beta_C91__shared',
                                   'process_role': 'api',
                                   'arguments': 'existing single-Project '
                                                'API role startup '
                                                'arguments',
                                   'routes': ['GET /health',
                                              'GET /tools',
                                              'GET /jobs/worker-runs',
                                              'POST /tools']},
                   'shared_api': {'transport': 'http',
                                  'socket': 'private Unix socket',
                                  'runner': 'managed_python',
                                  'module': 'API_MIXER_beta_C91.shared_runtime',
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

Serve the installed Tool capabilities through private HTTP, including
query, Workspace, View, saved SQL, projection, and Atom lifecycle operations.
MCP maps the catalog to its transport and forwards calls and results.
Enforce the selected Project's Tool blacklist.

For direct `GET /jobs/worker-runs`, require exactly one `instance_id`
matching the pinned Project. Validate the Worker Runs response against its
typed model before returning it.

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

### Export the Current shared Tool API at build time

#### Guarantee

Read the packaged Current Tool registry and Framework Version. Emit an
OpenAPI 3.1 document for public `GET /` and `POST /` on stdout.
Use the same descriptor adapter as the shared Backend for the catalog example.

Describe the Project-bound request and response envelopes. Use the registry
for examples. The admitted Projects can supply additional Tool names.
The shared Backend owns live Tool discovery and admission.

```python cli
declare_cli_contract(
    interface='current_openapi_export',
    action='export_current_tools',
    outcomes={'succeeded': 'zero', 'failed': 'nonzero'},
)
```
