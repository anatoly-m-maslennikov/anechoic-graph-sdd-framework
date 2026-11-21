# ANECHOIC Workbench MCP

The native MCP frontier contains the 28 Workbench tools for SQL queries,
Workspaces, Views, query history, the MCP App bridge, and Workbench service
control. Subject and Topic projection builders remain local tools; they do not
need MCP registration. Local and Public release run through `uv` on the host.
Set `project_mcp.release_workflows_enabled` to `True` in the native Project
Manifest to expose `local_release_command` and `public_release_command`.
The tools return shell commands for the selected Project. `False` or omission
blocks discovery and calls. See [Project release tools](../../FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/README.md).

Legacy Artifact search, specialized RMED revision, selected Workflow execution,
orchestration, capability discovery, Atom mutation, Revert, and graph Workflow
routes have been retired from this MCP frontier. Methodology/source Atoms,
including RMED contracts, have not yet been reconciled with this code retirement.

## Registration

`tool_providers.json` is the editable installed Provider inventory. It has
`schema_version`, `mcp_blacklist`, and `providers`; each Provider declares its
`provider_id`, Python `module`, `factory`, and `descriptor_factory`. Generate
the required checked-in `tool_registry.json` with:

```sh
uv run --project . --locked --no-sync --all-groups python -B \
  LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/generate_tool_registry.py \
  --package-root .
```

The generated registry pins the inventory digest and descriptor models. MCP
refuses startup when either asset is missing, malformed, stale, or does not
match installed Provider code. Adding a Provider or Tool requires an installed
implementation, one inventory entry, and regeneration; gateway routing stays
generic.

`factory(project_root, gateway)` is invoked lazily to create a Provider with
`call(name, arguments)` and `close()` methods. `descriptor_factory()` returns the corresponding
`mcp.types.Tool` models. The generated registry records `inventory_sha256`,
`mcp_blacklist`, Provider fields and descriptors, and `public_tools`.
The runtime validates each registered input schema before calling its Provider
and its output schema before returning the Provider result. A Provider may
optionally implement `prepare_arguments(name, arguments, context)` and
`present_result(name, value, context)` for its own transport shaping; the
gateway never applies Workbench-specific URL behavior to other Providers.

`mcp_blacklist` denies exact public Tool names globally. Project
`project_mcp.tool_blacklist` is unioned with it, so a Project cannot re-enable
a global denial. Both lists affect advertisement and direct invocation.

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
Component ID or a case-insensitive Manifest name. Contracts and Solutions
list Active Spec Atoms owned by the Component at Tier 0 and Tier 1.
Use the ID if names coincide. The `components` table exposes Manifest
settings and source references for custom SQL. Purpose lookup uses
the Component ID declared by an Active `component_purpose` Atom.

## Run

Use the project-local environment from the source checkout:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/.anechoic_runtime/launcher-venv" \
uv run --project "$PWD" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group rmed-workflow-mcp python \
  LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/server.py --project-root "$PWD"
```

The default transport is local stdio, and the host owns its process lifetime.
This command does not register MCP with a host or refresh an installed runtime.
For runtime installation and the isolated Docker HTTP transport, use
[Project release tools](../FEATURE_PROJECT_TOOLS/README.md) and the
[Docker runtime README](docker/README.md).

## Health and restart

The configured loopback listener serves JSON readiness at `GET /health`.
Explicit `Accept: text/html` requests receive a browser health page with
Workbench restart and reread controls. Restart the MCP process or container
after changing gateway code; implementation reload is retired. Workbench source
synchronization and its restart/reread tools remain independent.
