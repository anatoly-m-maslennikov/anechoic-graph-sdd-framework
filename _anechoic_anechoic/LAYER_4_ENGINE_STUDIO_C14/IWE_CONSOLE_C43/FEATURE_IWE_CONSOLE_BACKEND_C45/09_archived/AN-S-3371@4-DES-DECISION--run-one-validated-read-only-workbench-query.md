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
  status: archived
  version: 4
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---

## Summary

Run one validated read-only Workbench query

## Claim

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

## Semantics

Delegate only to the Kernel bound to the selected Project.


## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
