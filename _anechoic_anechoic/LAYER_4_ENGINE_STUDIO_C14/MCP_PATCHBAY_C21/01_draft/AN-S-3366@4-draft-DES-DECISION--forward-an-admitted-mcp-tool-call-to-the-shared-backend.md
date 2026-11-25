---
atom_family: SPEC
atom_id: AN-S-3366
container:
  component: C21
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3191@6-draft
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T10:58:19Z'
---

## Summary

Forward an admitted MCP Tool call to the shared Backend

## Claim

### Prose Claim

MCP forwards the Tool name, arguments, and caller context to the selected
native or Beta Backend. It returns the Backend result or a failure.

For a successful call, record the admitted Project binding, Backend request
validation, and Backend delegation before the selected Backend completes.
These effect targets classify observations across either Backend. They do
not replace the selected Backend's completion event.

In shared Beta mode, send the bound call to the shared Workbench API.
Receive the raw Tool result before returning MCP success. The pinned
Project Workbench API and the native Backend keep their own bindings.

For Workbench View Run, validate the Project binding before delegating to
Backend. Forward the completed query ID and metadata before returning
success. On save failure, forward the save error before reporting a partial
outcome. Report query failure without a completed result ID or a save error.

### Formal Claim

```python
component_workflow(
    component='C21',
    action='mcp_forward_tool',
    machine={
        'id': 'c21_mcp_forward_tool',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'mcp_tool_call': {'target': 'binding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'binding': {'on': {
                'project_admitted': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.project_binding', 'outcome': 'admitted'}}},
                'tool_call_refused_or_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.mcp_error', 'outcome': 'returned'}}},
            }},
            'validating': {'on': {
                'request_validated': {'target': 'delegating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'Backend.validation', 'outcome': 'validated'}}},
                'tool_call_refused_or_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.mcp_error', 'outcome': 'returned'}}},
            }},
            'delegating': {'on': {
                'request_delegated': {'target': 'forwarding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'Backend.delegation', 'outcome': 'delegated'}}},
                'tool_call_refused_or_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.mcp_error', 'outcome': 'returned'}}},
            }},
            'forwarding': {'on': {
                'backend_call_completed': [
                    {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'target': 'C45', 'outcome': 'succeeded'}}},
                    {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'target': 'C70', 'outcome': 'succeeded',
                         'detail': {'interface': 'workbench_api'}}}},
                ],
                'shared_beta_tool_call_sent': {'target': 'waiting_shared_beta', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70', 'outcome': 'requested',
                     'detail': {'interface': 'shared_workbench_api', 'transport': 'http',
                                'route': 'POST /tools', 'action': 'beta_backend_tool_call'}}}},
                'tool_call_refused_or_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.mcp_error', 'outcome': 'returned'}}},
            }},
            'waiting_shared_beta': {'on': {
                'shared_beta_tool_result_received': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.raw_tool_result', 'outcome': 'returned',
                     'detail': {'component': 'C70', 'action': 'beta_backend_tool_call',
                                'output': 'succeeded'}}}},
                'tool_call_refused_or_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.mcp_error', 'outcome': 'returned'}}},
            }},
            'responding': {'on': {
                'tool_result_returned': {'target': 'reporting_success', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.mcp_result', 'outcome': 'returned'}}},
            }},
            'reporting_success': {'on': {
                'tool_call_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reporting_error': {'on': {
                'tool_call_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```


```python
component_workflow(
    component='C21',
    action='workbench_view_run',
    machine={
        'id': 'c21_workbench_view_run',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'view_run_received': {'target': 'binding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'workbench_http',
                     'detail': {'transport': 'http', 'route': 'POST /anechoic/{project_name}/api/view_run',
                                'operation': 'view_run'}}}},
            }},
            'binding': {'on': {
                'project_admitted': {'target': 'delegating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.project_binding', 'outcome': 'admitted'}}},
                'view_run_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'delegating': {'on': {
                'view_run_delegated': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'Backend.view_run', 'outcome': 'delegated'}}},
                'view_run_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'running': {'on': {
                'query_id_returned': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned'}}},
                'run_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'completed': {'on': {
                'run_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'save_error_returned': {'target': 'save_error_reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.save_error', 'outcome': 'returned'}}},
            }},
            'save_error_reported': {'on': {
                'save_failed': {'target': 'partial', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'partial'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
            'partial': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
