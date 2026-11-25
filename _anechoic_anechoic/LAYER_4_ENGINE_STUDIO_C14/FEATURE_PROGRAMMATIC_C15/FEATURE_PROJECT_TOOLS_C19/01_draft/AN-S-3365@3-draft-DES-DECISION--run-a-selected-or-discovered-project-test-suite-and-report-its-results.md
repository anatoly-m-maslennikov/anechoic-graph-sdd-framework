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
  - AN-S-3287@8-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T09:04:52Z'
---

## Summary

Run a selected or discovered Project Test Suite and report its results.

## Claim

### Prose Claim

Discover or select test Modules. Run each Module in a fresh interpreter.
Collect each Module result and report the suite totals.

For each terminal output, classify the process status before recording
it as `exit_status_class` in the trace.

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
                'suite_requested': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'trigger',
                    'target': 'test_suite',
                    'detail': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py',
                    },
                }}},
            }},
            'selecting': {'on': {
                'run_selected_tests': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19'}}},
                'invalid_selection_or_environment': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_status_class': 'nonzero'}}}},
            }},
            'running': {'on': {
                'suite_passed': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {'exit_status_class': 'zero'}}}},
                'suite_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_status_class': 'nonzero'}}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```
