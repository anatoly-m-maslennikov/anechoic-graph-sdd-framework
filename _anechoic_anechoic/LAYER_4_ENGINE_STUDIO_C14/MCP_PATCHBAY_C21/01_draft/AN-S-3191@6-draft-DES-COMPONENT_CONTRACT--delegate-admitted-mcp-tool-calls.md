---
atom_family: SPEC
atom_id: AN-S-3191
container:
  component: C21
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3044
state:
  status: draft
  version: 6
  updated_at: '2026-11-25T10:58:19Z'
---

## Summary

Delegate admitted MCP Tool calls

## Guarantee

For an admitted Project, expose the Tools in the Backend JSON catalog.
Preserve each Tool's name, description, and input schema. Forward the
Tool name, arguments, and request context to Backend and return its
result or failure through MCP.

Expose the same delegation over stdio and Streamable HTTP. In shared
HTTP mode bind each call to its explicit Project. Keep the request's
session and public URL context with the bound call.

Backend owns Tool eligibility, validation, and dispatch. MCP can read the
Project Manifest and runtime settings through declared interfaces for
Project binding and startup. The MCP bridge has zero production
cross-Component imports.

Every Finder and every Doer dry run must remain independently executable
without MCP. A direct executable invocation of an ANECHOIC Markdown Atom
Doer with `--apply` must reject the request unless it carries the authorized
project-local MCP delegation and its sealed Initiative action envelope.

## Claim

### Prose Claim

A successful forwarded call records an admitted Project binding, Backend
request validation, and Backend delegation. The trace names those effects
`C21.project_binding`, `Backend.validation`, and `Backend.delegation`.
These names classify observations; they do not select a Backend.

The MCP trace leaves Tool arguments, request context, result values,
and security conditions as prose guarantees.

The Workbench HTTP interface validates the selected Project and delegates
`view_run` to its Backend. The Backend validates and runs one whole
read-only View query. A completed Run returns its query ID, counts and
metadata. Fetch rows separately.

A failed query has neither a completed result ID nor a save error. A later
save failure retains the query ID and metadata and reports a partial outcome.

### Formal Claim

```python trace
declare_trace_contract(
    action='mcp_forward_tool',
    output='succeeded',
    must_effect=(('C21.project_binding', 'admitted'),
                 ('Backend.validation', 'validated'),
                 ('Backend.delegation', 'delegated'),
                 ('C21.mcp_result', 'returned')),
    must_precede=((('C21.project_binding', 'admitted'), ('Backend.validation', 'validated')),
                  (('Backend.validation', 'validated'), ('Backend.delegation', 'delegated')),
                  (('Backend.delegation', 'delegated'), ('C21.mcp_result', 'returned'))),
)
```


```python trace
declare_trace_contract(
    action='mcp_forward_tool',
    output='failed',
    must_effect=(('C21.mcp_error', 'returned'),),
    forbid_effect=('C21.mcp_result',),
)
```

```python trace
declare_trace_contract(
    action='workbench_view_run',
    interface='workbench_http',
    route='POST /anechoic/{project_name}/api/view_run',
    transport='http',
    operation='view_run',
    output='succeeded',
    must_effect=(('C21.project_binding', 'admitted'),
                 ('Backend.view_run', 'delegated'),
                 ('C21.view_run.query_id', 'returned')),
    forbid_effect=('C21.view_run.save_error',),
    must_precede=((('C21.project_binding', 'admitted'), ('Backend.view_run', 'delegated')),
                  (('Backend.view_run', 'delegated'), ('C21.view_run.query_id', 'returned'))),
)
```

```python trace
declare_trace_contract(
    action='workbench_view_run',
    interface='workbench_http',
    route='POST /anechoic/{project_name}/api/view_run',
    transport='http',
    operation='view_run',
    output='partial',
    must_effect=(('C21.project_binding', 'admitted'),
                 ('Backend.view_run', 'delegated'),
                 ('C21.view_run.query_id', 'returned'),
                 ('C21.view_run.save_error', 'returned')),
    must_precede=((('C21.project_binding', 'admitted'), ('Backend.view_run', 'delegated')),
                  (('Backend.view_run', 'delegated'), ('C21.view_run.query_id', 'returned')),
                  (('C21.view_run.query_id', 'returned'), ('C21.view_run.save_error', 'returned'))),
)
```

```python trace
declare_trace_contract(
    action='workbench_view_run',
    interface='workbench_http',
    route='POST /anechoic/{project_name}/api/view_run',
    transport='http',
    operation='view_run',
    output='failed',
    forbid_effect=('C21.view_run.query_id', 'C21.view_run.save_error'),
)
```
