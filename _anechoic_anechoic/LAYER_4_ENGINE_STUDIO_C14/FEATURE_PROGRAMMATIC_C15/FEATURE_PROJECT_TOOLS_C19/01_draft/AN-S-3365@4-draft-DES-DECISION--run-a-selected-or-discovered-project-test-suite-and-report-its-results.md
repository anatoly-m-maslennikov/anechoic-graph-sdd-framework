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
  - AN-S-3287@9-draft
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T09:04:52Z'
---

## Summary

Run a selected or discovered Project Test Suite and report its results.

## Claim

### Prose Claim

Discover or select test Modules. Run each Module in a fresh interpreter.
Collect each Module result and report the suite totals.

For each terminal output, classify the process status before recording
it as `exit_status_class` in the trace. Record a failed release test phase
before reporting its failure.

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

```python
component_workflow(
    component='C19', action='run_release_test_phase',
    machine={
        'id': 'c19_run_release_test_phase', 'initial': 'idle',
        'states': {
            'idle': {'on': {
                'static_selected': {'target': 'static_testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'test_suite', 'detail': {'phase': 'static'}}}},
                'functional_selected': {'target': 'functional_testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'test_suite', 'detail': {'phase': 'functional'}}}},
                'image_selected': {'target': 'image_testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'test_suite', 'detail': {'phase': 'image'}}}},
            }},
            'static_testing': {'on': {
                'static_checks_passed': {'target': 'static_pass', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'static_checks', 'outcome': 'passed'}}},
                'static_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'failed'}}},
            }},
            'functional_testing': {'on': {
                'functional_checks_passed': {'target': 'functional_pass', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'host_functional_checks', 'outcome': 'passed'}}},
                'functional_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'failed'}}},
            }},
            'image_testing': {'on': {
                'candidate_tests_passed': {'target': 'canary_testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'candidate_image_tests', 'outcome': 'passed'}}},
                'image_tests_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'failed'}}},
            }},
            'canary_testing': {'on': {
                'canary_passed': {'target': 'image_pass', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'candidate_canary', 'outcome': 'passed'}}},
                'canary_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'failed'}}},
            }},
            'reporting_failure': {'on': {
                'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'static_pass': {'on': {
                'static_phase_passed': {'target': 'reporting_static', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
            }},
            'functional_pass': {'on': {
                'functional_phase_passed': {'target': 'reporting_functional', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
            }},
            'image_pass': {'on': {
                'image_phase_passed': {'target': 'reporting_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
            }},
            'reporting_static': {'on': {
                'static_result': {'target': 'static_passed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'static_passed'}}},
            }},
            'reporting_functional': {'on': {
                'functional_result': {'target': 'functional_passed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'functional_passed'}}},
            }},
            'reporting_image': {'on': {
                'image_result': {'target': 'image_passed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'image_passed'}}},
            }},
            'static_passed': {'type': 'final'}, 'functional_passed': {'type': 'final'},
            'image_passed': {'type': 'final'}, 'failed': {'type': 'final'},
        },
    },
)
```
