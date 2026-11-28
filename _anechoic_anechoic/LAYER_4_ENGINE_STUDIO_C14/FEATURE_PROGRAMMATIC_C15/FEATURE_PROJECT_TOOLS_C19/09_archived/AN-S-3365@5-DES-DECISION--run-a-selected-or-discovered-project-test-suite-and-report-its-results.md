---
atom_family: SPEC
atom_id: AN-S-3365
container:
  component: C19
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3287@8
state:
  status: archived
  version: 5
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---

## Summary

Run a selected or discovered Project Test Suite and report its results.

## Claim

### Prose Claim

The suite validates its request, discovers or selects test modules, runs
them in fresh interpreters, and returns results and a status.

### Formal Claim

```python
component_workflow(
    component='C19',
    action='run_project_test_suite',
    machine={
        'id': 'c19_run_project_test_suite',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'suite_requested': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'selecting': {'on': {
                'run_selected_tests': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19'}}},
                'invalid_selection_or_environment': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'running': {'on': {
                'suite_passed': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'suite_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

Use AN-S-2686 for trace evidence.
