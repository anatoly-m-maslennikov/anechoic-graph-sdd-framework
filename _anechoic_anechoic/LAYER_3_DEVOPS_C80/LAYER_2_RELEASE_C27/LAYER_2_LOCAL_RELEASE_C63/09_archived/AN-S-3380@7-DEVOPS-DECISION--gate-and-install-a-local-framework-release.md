---
atom_family: SPEC
atom_id: AN-S-3380
container:
  component: C63
tier: 1
context:
  template: DECISION
  lens: DevOps
relations:
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@2
  IS_SOLUTION_FOR:
  - AN-S-3292@11
state:
  status: archived
  version: 7
  updated_at: '2026-11-24T13:51:38.603869+00:00'
---

## Summary

Gate and install a local Framework release.

## Claim

### Prose Claim

Local Release checks prerequisites and runs the required host gates.
An explicit target run pins its source revision separately and verifies
the target-owned candidate before installation.
The standalone image gate ends with verification evidence.

Resume keeps the run's candidate version and reuses verified evidence.
Continue at the earliest incomplete or invalidated phase.

### Formal Claim

This claim covers a fresh same-Project run.

```python
component_workflow(
    component='C63',
    action='run_local_release',
    machine={
        'id': 'c63_run_local_release',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'local_release_requested': {'target': 'preparing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'preparing': {'on': {
                'inputs_validated_and_version_bumped': {'target': 'testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
                'preparation_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'testing': {'on': {
                'static_and_host_functional_tests_passed': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
                'tests_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'building': {'on': {
                'candidate_image_prepared': {'target': 'verifying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
                'build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'verifying': {'on': {
                'candidate_image_verified': {'target': 'installing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
                'verification_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'installing': {'on': {
                'runtime_installed_and_started': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
                'installation_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reporting': {'on': {
                'finalization_failed': {'target': 'failed', 'guard': {
                    'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}},
                'release_completed': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed'}}},
                'release_cleanup_pending': {'target': 'cleanup_pending', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed_with_cleanup_pending'}}},
            }},
            'completed': {'type': 'final'},
            'failed': {'type': 'final'},
            'cleanup_pending': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
