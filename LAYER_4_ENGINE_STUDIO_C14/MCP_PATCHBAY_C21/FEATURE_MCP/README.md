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
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project LAYER_3_ENVIRONMENTS_C72/engine --locked --no-sync --group dev python -B -P -m \
  IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.generate_tool_registry \
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
Component ID or a case-insensitive Manifest name. Contracts and Solutions
list Current Spec Atoms directly owned by the Component. Contracts include
Tier 0 Atoms and Tier 1 `component_contract` Atoms. Solutions include other
Tier 1 Atoms.
Use the ID if names coincide. The `components` table exposes Manifest
settings and source references for custom SQL. Purpose lookup returns the
Component Manifest when it contains a `## Purpose` section with prose.

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

## Component Contract lifecycle

Use `atom_lifecycle_create_draft` with `newAtom.template` set to
`component_contract`. Supply `newAtom.container.component` as the Component ID,
`newAtom.lens` as an enabled Lens, and `newAtom.body` as Markdown with
`## Summary` and a nonempty `## Guarantee`. The tool sets Tier 1.

Use the exact Draft reference and version from `savedDraft` with
`atom_lifecycle_promote_draft` to publish the Contract. Put its exact Current
revision in the `implements` list of the owning Component Package's
`<package-folder-name>__spec_bind.yaml`. Workbench reports coverage for each
Current Contract in `package_audit.component_contracts`.

## Run

Use the project-local environment from the source checkout:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project "$PWD/LAYER_3_ENVIRONMENTS_C72/engine" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group dev python -B -P -m \
  MCP_PATCHBAY_C21.FEATURE_MCP.server --project-root "$PWD"
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
