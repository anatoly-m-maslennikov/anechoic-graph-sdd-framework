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
  - AN-S-4794@1
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Run a View through the Project Workbench

## Claim

### Prose Claim

The browser submits a View Run to the selected Project interface. The Backend
validates the operation and delegates the query to the Project Kernel. The
browser displays the result or reports a failure.

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
                    {'kind': 'effect', 'target': 'C45', 'outcome': 'succeeded'}}},
                'project_run_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'displaying': {'on': {
                'result_displayed': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'display_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution describes the cross-Component flow. Trace conformance requires
recorded evidence.
