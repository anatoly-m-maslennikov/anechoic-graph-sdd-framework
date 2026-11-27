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
  - AN-S-3185@11
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-27T14:43:25.838139+00:00"
---

## Summary

Run one validated read-only Workbench query

## Claim

### Prose Claim

Backend validates Run arguments and delegates the query to the selected
Project Kernel, then returns its result or failure.

### Formal Claim

```python
component_workflow(
    component='C45',
    action='workbench_backend_run_query',
    machine={
        'id': 'c45_workbench_backend_run_query',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'query_run_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'validating': {'on': {
                'valid_run_delegated': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded'}}},
                'invalid_run_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'executing': {'on': {
                'query_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'query_execution_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
