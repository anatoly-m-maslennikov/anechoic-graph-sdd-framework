---
atom_family: SPEC
atom_id: AN-S-3377
container:
  component: C59
tier: 1
context:
  template: DECISION
  lens: SPEC
relations:
  IS_SOLUTION_FOR:
  - AN-S-3305@3-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:58:34Z'
---

## Summary

Run a Workbench query against the native Project store.

## Claim

### Prose Claim

For a successful unsaved Run, the Kernel selects the statement and retains
the query result. It attempts to enqueue a log entry before delivery. A
logging error can leave the result usable. A foreign Project binding is
rejected before a statement is selected.

### Formal Claim

```python
component_workflow(
    component='C59',
    action='kernel_run_query',
    machine={
        'id': 'c59_kernel_run_query',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'query_requested': {'target': 'admitting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'database_api',
                     'detail': {'transport': 'http', 'route': 'POST /database',
                                'operation': 'operation', 'save': False}}}},
            }},
            'admitting': {'on': {
                'project_admitted': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59.project_binding', 'outcome': 'admitted'}}},
                'foreign_project_rejected': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59.project_binding', 'outcome': 'rejected'}}},
            }},
            'selecting': {'on': {
                'statement_selected': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59.statement', 'outcome': 'selected'}}},
            }},
            'running': {'on': {
                'query_result_retained': {'target': 'logging', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59.result', 'outcome': 'retained'}}},
            }},
            'logging': {'on': {
                'query_log_enqueue_attempted': {'target': 'delivering', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59.query_log', 'outcome': 'enqueue_attempted'}}},
            }},
            'delivering': {'on': {
                'query_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'rejecting': {'on': {
                'rejection_returned': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'rejected'}}},
            }},
            'succeeded': {'type': 'final'},
            'rejected': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
The added evidence distinguishes Project admission, statement selection, result
retention, and the logging attempt. Trace conformance requires recorded evidence.
