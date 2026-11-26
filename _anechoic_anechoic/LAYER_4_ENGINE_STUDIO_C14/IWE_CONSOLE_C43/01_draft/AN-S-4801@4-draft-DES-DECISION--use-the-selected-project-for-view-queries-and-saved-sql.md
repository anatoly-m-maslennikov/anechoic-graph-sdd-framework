---
atom_family: SPEC
atom_id: AN-S-4801
container:
  component: C43
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4794@2-draft
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T10:59:12.782847+00:00'
---

## Summary

Run a View through the Project Workbench

## Claim

### Prose Claim

The browser submits a View Run to the selected Project interface. The Backend
validates the operation and delegates the query to the Project Kernel. The
browser displays the result or reports a failure. If the query completes but
Save fails, the browser displays the save error and the result, and reports a
partial outcome.

The native path delegates query dispatch to C45 behind C21. The browser
consumes the Project HTTP response and C46 owns the display.

### Formal Claim

```python
component_workflow(
    component='C43',
    action='workbench_run_view',
    machine={
        'id': 'c43_workbench_run_view',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'run_selected': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'running': {'on': {
                'project_run_succeeded': {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run',
                                'output': 'succeeded'}}}},
                'project_run_partial': {'target': 'partial_save_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run',
                                'output': 'partial'}}}},
                'project_run_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_save_error': {'on': {
                'project_save_error_returned': {'target': 'showing_partial_save_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.save_error', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run',
                                'output': 'partial'}}}},
                'project_run_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'showing_partial_save_error': {'on': {
                'partial_save_error_displayed': {'target': 'partial_displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_save_error', 'outcome': 'shown',
                     'detail': {'component': 'C46', 'action': 'workbench_frontend_run_view',
                                'output': 'partial'}}}},
                'partial_save_error_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_displaying': {'on': {
                'partial_result_displayed': {'target': 'partial_displayed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_display', 'outcome': 'shown',
                     'detail': {'component': 'C46', 'action': 'workbench_frontend_run_view',
                                'output': 'partial'}}}},
                'partial_display_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_displayed': {'on': {
                'run_partial': {'target': 'partial', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'partial'}}},
            }},
            'displaying': {'on': {
                'result_displayed': {'target': 'displayed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_display', 'outcome': 'shown',
                     'detail': {'component': 'C46', 'action': 'workbench_frontend_run_view',
                                'output': 'succeeded'}}}},
                'display_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'displayed': {'on': {
                'run_completed': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'partial': {'type': 'final'},
            'succeeded': {'type': 'final'},
            'reporting_error': {'on': {
                'run_error_reported': {'target': 'finishing_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run_failure', 'outcome': 'reported'}}},
            }},
            'finishing_failure': {'on': {
                'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution describes the cross-Component flow. Trace conformance requires
recorded evidence.
