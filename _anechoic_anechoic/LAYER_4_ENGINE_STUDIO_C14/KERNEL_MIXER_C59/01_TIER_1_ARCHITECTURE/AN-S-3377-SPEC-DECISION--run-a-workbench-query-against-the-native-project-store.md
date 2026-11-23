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
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@2
  IS_SOLUTION_FOR:
  - AN-S-3305@2
state:
  status: active
  version: 2
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---

## Summary

Run a Workbench query against the native Project store.

## Claim

### Prose Claim

For a successful unsaved Run, the Kernel selects the statement and retains
the query result. It attempts to enqueue a log entry before delivery. A
logging error can leave the result usable.

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
                'query_requested': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'save': False}}}},
            }},
            'running': {'on': {
                'query_result_retained': {'target': 'logging', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59'}}},
            }},
            'logging': {'on': {
                'query_log_enqueue_attempted': {'target': 'delivering', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59'}}},
            }},
            'delivering': {'on': {
                'query_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
