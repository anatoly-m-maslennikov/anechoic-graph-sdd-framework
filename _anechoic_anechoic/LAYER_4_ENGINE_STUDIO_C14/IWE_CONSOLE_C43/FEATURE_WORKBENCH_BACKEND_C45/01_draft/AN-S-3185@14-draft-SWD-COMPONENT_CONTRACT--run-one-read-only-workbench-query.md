---
atom_family: SPEC
atom_id: AN-S-3185
container:
  component: C45
tier: 0
context:
  template: component_contract
  lens: SWD
relations:
  ANSWERS:
  - AN-S-3059
state:
  status: draft
  version: 14
  updated_at: '2026-11-25T01:30:17.431692+00:00'
---

## Summary

Run one read-only Workbench query

## Guarantee

Reject invalid inputs and report query execution failures.

## Interface

The Python module is
`IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.backend_process`.
Run it for one pinned Project Backend.

The launcher supports optional `--host-project-root`,
`--default-workbench-storage` with `disk` or `memory`, and
`--default-journal-storage` with `files` or `duckdb`. The parent owns the
process lifetime. Closing the child's stdin produces EOF for the
parent-watch channel and requests Backend shutdown.

When supplied, `asserted_project_root`, `public_base_url`, and `session_id`
are nonblank strings. The asserted Project root must match the bound Project
root or host root.

## Tool API

Publish the enabled Tool names, descriptions, and schemas for an admitted
Project. Use the same registry to validate and dispatch named calls.
Return the Tool result or a failure for a stale registry, disabled Tool,
or invalid request.

## Claim

This claim covers three selected outcomes of `POST /tools`; other Tool
failures retain their existing error semantics.

Forward Worker status requests to C66. Return both active runs and
latest terminal runs. The status request is read-only. Response field
names and behavior for missing or foreign bindings remain open.

### Formal Claim

```python contract
declare_contract(
    operation="POST /tools",
    outcomes={
        "success": (200, "result"),
        "invalid_input": (400, "typed_error"),
        "internal_error": (500, "typed_error"),
    },
    checks={
        "interface": {
            "protocol": "http",
            "transport": "unix_socket",
            "request_format": "json",
            "response_format": "json",
            "cli_required": (
                "--control-root",
                "--instance-id",
                "--manifest-sha256",
                "--project-root",
                "--socket",
            ),
        },
        "input_format": {
            "fields": (
                "arguments",
                "asserted_project_root",
                "instance_id",
                "name",
                "public_base_url",
                "session_id",
            ),
            "name": "string",
            "arguments": "object",
            "nullable_strings": (
                "asserted_project_root",
                "public_base_url",
                "session_id",
            ),
        },
        "output_format": {
            "result_fields": ("text", "value"),
            "value": "object",
            "text": "string_or_null",
        },
        "error_handling": {
            "error_fields": ("code", "message", "tool_result"),
            "internal_message": "Backend Tool operation failed",
        },
        "preconditions": {
            "project_binding": "matching_instance",
            "tool": "enabled_and_in_registry",
        },
        "guarantees": {
            "query": "one_complete_read_only_statement",
            "query_output": "requested_delivery_without_submitted_sql",
        },
        "effects": {
            "invalid_input_dispatch": "none",
            "query_result": "retained",
            "bookmark": "explicit_save_only",
        },
    },
)
```


```python trace
declare_trace_contract(
    action='workbench_backend_worker_status',
    interface='workbench_api',
    transport='http',
    route='GET /jobs/worker-runs',
    operation='worker_runs',
    output='succeeded',
    must_effect=(('C66', 'requested'),
                 ('C66.active_runs', 'returned'),
                 ('C66.latest_terminal_runs', 'returned')),
    forbid_effect=('C66.worker_process', 'C66.worker_run'),
    must_precede=((('C66', 'requested'), ('C66.active_runs', 'returned')),
                  (('C66', 'requested'), ('C66.latest_terminal_runs', 'returned'))),
)
```

## Semantics

- `typed_error` is a structured error. Its `code` is machine-readable, its
  `message` is caller-safe, and `tool_result` carries outcome and diagnostics.
  `internal_error` is an unexpected failure during request handling that
  prevents successful completion.
- `matching_instance` means equality with the admitted Project identity.
  `enabled_and_in_registry` means the Tool is enabled in the current registry.
- `one_complete_read_only_statement` means the entire SQL is parsed as one
  read-only query against the selected Project. Cursor metadata does not
  slice the SQL.
- `requested_delivery_without_submitted_sql` returns result metadata in the
  requested inline, file, or automatic delivery and result format without
  echoing submitted SQL.
- `none` means invalid input is rejected before the provider call.
- `retained` means the result remains accessible by its returned `query_id`
  for paging under existing retention.
- `explicit_save_only` means a Bookmark exists only when the causal request
  sets `save: true`.

## Process boundary

Resolve the requested Project and return its Manifest pin and verified
host binding without opening DuckDB. Return its normalized Tool blacklist and
release workflow enablement.

Serve one admitted Project per Backend process over a private Unix
socket. Check the Project Manifest revision and instance identity before
readiness. Validate named Workbench operations in the Backend and call
the Project's Kernel to execute queries and publish lifecycle updates.
When release workflows are enabled, revalidate the Project Manifest pin and
return the host command for the declared local or public Release entrypoint.

Use the Project Manifest's storage settings first, then the host
defaults. The caller owns the process lifetime and closes it when the
Project leaves the pool or the caller exits.

## Shared host

The Backend coordinator reads the host settings, resolves explicit Project
roots, and publishes the compatible Tool catalog. It routes a named call
only to its selected Project. It holds a bounded pool of Project Backend
processes and closes them on eviction or shutdown.

MCP uses the private Unix socket for status, selection, catalog, and calls.
The configured host settings must remain current for Project calls.
