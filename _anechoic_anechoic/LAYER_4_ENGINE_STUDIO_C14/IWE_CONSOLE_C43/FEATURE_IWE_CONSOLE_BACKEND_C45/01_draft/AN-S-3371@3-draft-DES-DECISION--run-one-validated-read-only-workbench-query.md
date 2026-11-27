---
atom_family: SPEC
atom_id: AN-S-3371
container:
  component: C45
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3185@14-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T01:30:17.431692+00:00'
---

## Summary

Run one validated read-only Workbench query

## Claim

### Formal Claim

```python
component_workflow(
    component='C45',
    action='workbench_backend_run_query',
    startup={
        'required_arguments': ['--socket', '--project-root', '--control-root',
                               '--instance-id', '--manifest-sha256'],
    },
    machine={
        'id': 'c45_workbench_backend_run_query',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'query_run_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'trigger',
                    'detail': {
                        'operation': 'POST /tools',
                        'protocol': 'http',
                        'transport': 'unix_socket',
                        'request_format': 'json',
                        'request_fields': ['name', 'arguments', 'instance_id', 'session_id',
                                           'public_base_url', 'asserted_project_root'],
                    },
                }}},
            }},
            'validating': {'on': {
                'valid_run_delegated': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded',
                    'detail': {
                        'interface': 'database_api', 'transport': 'http',
                        'route': 'POST /database', 'operation': 'operation',
                        'input_types': {
                            'name': 'string',
                            'arguments': 'object',
                            'nullable_strings': ['asserted_project_root', 'public_base_url', 'session_id'],
                        },
                        'matches_admitted_instance': True,
                        'tool_enabled': True,
                        'tool_in_registry': True,
                        'sql': {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True},
                    },
                }}},
                'invalid_run_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'output', 'outcome': 'failed',
                    'detail': {'http_outcome': 'invalid_input', 'status_code': 400, 'envelope': 'typed_error',
                               'response_format': 'json', 'response_fields': ['code', 'message', 'tool_result'],
                               'provider_dispatched': False},
                }}},
                'validation_failed_unexpectedly': {'target': 'failing', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'effect', 'outcome': 'failed', 'detail': {'failure': 'internal_error'},
                }}},
            }},
            'executing': {'on': {
                'query_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'output', 'outcome': 'succeeded',
                    'detail': {
                        'http_outcome': 'success', 'status_code': 200, 'envelope': 'result',
                        'response_format': 'json', 'response_fields': ['text', 'value'],
                        'result_types': {'text': 'string_or_null', 'value': 'object'},
                        'delivery_mode': 'requested',
                        'include_submitted_sql': False,
                        'retain_result_by': 'query_id',
                        'bookmark_requires_save': True,
                    },
                }}},
                'query_execution_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'output', 'outcome': 'failed', 'detail': {'failure': 'tool_failure'},
                }}},
                'execution_failed_unexpectedly': {'target': 'failing', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'effect', 'outcome': 'failed', 'detail': {'failure': 'internal_error'},
                }}},
            }},
            'failing': {'on': {
                'internal_error_returned': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'output', 'outcome': 'failed',
                    'detail': {'http_outcome': 'internal_error', 'status_code': 500, 'envelope': 'typed_error',
                               'response_format': 'json', 'response_fields': ['code', 'message', 'tool_result'],
                               'message': 'Backend Tool operation failed'},
                }}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```


```python
component_workflow(
    component='C45',
    action='workbench_backend_worker_status',
    machine={
        'id': 'c45_workbench_backend_worker_status',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'worker_status_requested': {'target': 'forwarding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'workbench_api', 'detail': {
                        'transport': 'http', 'route': 'GET /jobs/worker-runs', 'operation': 'worker_runs',
                    }}}},
            }},
            'forwarding': {'on': {
                'worker_status_forwarded': {'target': 'receiving', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66', 'outcome': 'requested', 'detail': {
                        'interface': 'worker_runs', 'transport': 'http',
                        'route': 'GET /jobs/worker-runs', 'operation': 'worker_runs',
                        'action': 'manifest_compiler_worker_status',
                    }}}},
            }},
            'receiving': {'on': {
                'worker_active_runs_received': {'target': 'await_terminal_runs', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.active_runs', 'outcome': 'returned', 'detail': {
                        'component': 'C66', 'action': 'manifest_compiler_worker_status', 'output': 'succeeded',
                    }}}},
                'worker_terminal_runs_received': {'target': 'await_active_runs', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.latest_terminal_runs', 'outcome': 'returned', 'detail': {
                        'component': 'C66', 'action': 'manifest_compiler_worker_status', 'output': 'succeeded',
                    }}}},
            }},
            'await_terminal_runs': {'on': {
                'worker_terminal_runs_received': {'target': 'return_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.latest_terminal_runs', 'outcome': 'returned', 'detail': {
                        'component': 'C66', 'action': 'manifest_compiler_worker_status', 'output': 'succeeded',
                    }}}},
            }},
            'await_active_runs': {'on': {
                'worker_active_runs_received': {'target': 'return_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.active_runs', 'outcome': 'returned', 'detail': {
                        'component': 'C66', 'action': 'manifest_compiler_worker_status', 'output': 'succeeded',
                    }}}},
            }},
            'return_result': {'on': {
                'worker_status_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```

## Semantics

`tool_failure` follows the existing Tool failure behavior. `internal_error`
means an unexpected failure that prevents the request from completing.

The C59 delegation event carries the completed validation checks. Cursor
metadata locates text independently of the complete SQL submitted for validation.
The success event records how the result can be retrieved and whether a
request can create a Bookmark.
