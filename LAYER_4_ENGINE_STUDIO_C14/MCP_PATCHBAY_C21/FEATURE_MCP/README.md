# ANECHOIC Workbench MCP

The native MCP frontier contains the 28 Workbench tools for SQL queries,
Workspaces, Views, query history, the MCP App bridge, and Workbench service
control. Subject and Topic projection builders remain local tools; they do not
need MCP registration. Local and Public release run through `uv` on the host.
Set `project_mcp.release_workflows_enabled` to `True` in the native Project
Manifest to expose `local_release_command` and `public_release_command`.
The tools read the Active release Workflow Formal Claims in `__PROJECT_CONFIG`.
Each call returns one shell-quoted command for the Operator to run on the host.
`False` or omission blocks discovery and calls.
See [Project release tools](../../FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/README.md).

Legacy Artifact search, specialized RMED revision, selected Workflow execution,
orchestration, capability discovery, Atom mutation, Revert, and graph Workflow
routes have been retired from this MCP frontier. Methodology/source Atoms,
including RMED contracts, have not yet been reconciled with this code retirement.

## Registration

Backend owns the Tool provider inventory, generated registration asset, schema
validation, and Tool dispatch. MCP reads Backend's enabled JSON catalog and
maps each Tool's name, description, and input schema to MCP. It forwards the
Tool name, arguments, and request context to Backend and returns its result or
failure. A missing or invalid catalog fails explicitly.

The Backend's `tool_providers.json` is the editable installed Provider
inventory. Generate its checked-in `tool_registry.json` with:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked --no-sync --group dev python -B -P -m \
  IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.generate_tool_registry \
  --package-root .
```

Backend verifies the inventory and registry against installed Provider code.
Its global `mcp_blacklist` and Project `project_mcp.tool_blacklist` exclusions
apply to both discovery and invocation. A Project cannot re-enable a global
denial. Backend reports invalid or stale registration explicitly.

## Project context

Single-project calls accept an optional top-level `project_root` assertion. It
must match the trusted Project's canonical host root or declared container
mapping. The gateway validates and removes this outer field before dispatch.
Shared MCP requires `project_root`; protocol operations such as initialization
and listing do not.

## Native query templates

Use `query_template` for Atom lookups, state, search, revisions, inventory
and counts, relations, and legacy references or paths. For an Epic queue, pass
`{"template":"list_tickets","kind":"epic","statuses":["active","backlog","draft"]}`
or pass `parent` with a Ticket ID to list its direct children.
Each template runs through `query_run` with its own columns. Both tools
use automatic delivery by default. Workbench reads
`runtime.workbench.inline_result_limit_kib` from the Project Manifest at
startup. It defaults to 4 KiB. Automatic delivery returns results inline
when they fit within the first page and the byte limit. Templates
default to CSV and `query_run` defaults to `json_matrix`. Pass
`result_delivery: inline` or `result_delivery: file` to choose explicitly.

Use `component` with `fetch_contracts`, `fetch_solutions`,
`get_component_manifest`, or `get_component_purpose`. It accepts a
Component ID or a case-insensitive Manifest name. Contract lookup returns the
Component Manifest when it has a `## Component Contract` section. Solution
lookup returns Active Tier 0 Solution Atoms owned by the Component. Use the ID if
names coincide. The `components` table exposes Manifest settings and source
references for custom SQL. Purpose lookup returns the Component Manifest when
it contains a `## Purpose` section with prose.

## Planning Ticket lifecycle

Use `atom_lifecycle_create_draft` with `newAtom.template: task` and an
optional `newAtom.label`. The Ticket Model declares the navigation labels.
Use the stable ID of a Current planning Ticket or a first Draft as the
container when creating a child.

Publishing a first Draft to Backlog or Active, or activating a Backlog
Ticket, promotes lower-status planning descendants with it. Assets and
terminal descendants retain their statuses.

Use `list_tickets` with `label` to filter by navigation label. The result
reports Label separately from Template.

## Component Contract coverage

Put the Component Manifest's exact Current revision in the `implements` list
of the owning Component Package's `<package-folder-name>__spec_bind.yaml`.
Workbench reports coverage in `package_audit.component_contracts`.

## Run

Use the project-local environment from the source checkout:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group dev python -B -P -m \
  MCP_PATCHBAY_C21.FEATURE_MCP.server --project-root "$PWD"
```

The default transport is local stdio, and the host owns its process lifetime.
This command does not register MCP with a host or refresh an installed runtime.
For runtime installation and the isolated Docker HTTP transport, use
[Project release tools](../FEATURE_PROJECT_TOOLS/README.md) and the
[Docker runtime README](docker/README.md).

### Runtime profiles

Set `ANECHOIC_RUNTIME_PROFILE` to choose the Beta runtime settings. The local
host launcher defaults to `dev-local`. Beta images default to `dev-preprod`.

| Profile | Workbench | Journal | Archives |
| --- | --- | --- | --- |
| `dev-local` | `memory` | `files` | `skip` |
| `dev-preprod` | `disk` | `duckdb` | `load` |
| `test` | `memory` | `files` | `load` |
| `prod` | `disk` | `duckdb` | `load` |

Override each setting with `ANECHOIC_WORKBENCH_STORAGE`,
`ANECHOIC_JOURNAL_STORAGE`, or `ANECHOIC_ARCHIVES`. An environment profile takes
precedence over storage settings in the Project Manifest. Other Project
settings, such as the file Journal path, still come from the Manifest.

`skip` omits archived rows and Atom lifecycle mutations return
`archive_disabled`. Set `ANECHOIC_ARCHIVES=load` before launch to enable
history and lifecycle writes.

Set `ANECHOIC_WORKBENCH_STORAGE=disk` in `dev-local` to persist the Workbench in
`.anechoic_runtime/workbench/beta/`. Local filenames end in
`-dev-local-skip.duckdb` or `-dev-local-load.duckdb`. Each is separate from the
image's projection. Disk storage with `skip` is available in `dev-local`.

## Health and restart

The configured loopback listener serves JSON readiness at `GET /health`.
Explicit `Accept: text/html` requests receive a browser health page with
Workbench restart and reread controls. Restart the MCP process or container
after changing gateway code; implementation reload is retired. Workbench source
synchronization and its restart/reread tools remain independent.
