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
  - AN-S-3292@12
state:
  status: archived
  version: 8
  updated_at: '2026-11-24T18:03:32.256316+00:00'
---

## Summary

Gate and install a local Framework release.

## Claim

### Prose Claim

Local Release checks prerequisites, runs the host gates, builds the candidate,
and verifies the image suite and MCP canary as separate phases. Standalone
image verification ends with verification evidence.

Each continuation keeps the Run ID, target, and candidate version. Before
delivery, it accepts the corrected exact source revision and reuses each
passing phase whose inputs and evidence still match. After delivery starts,
it reconciles the recorded artifact before repeating an effect.

### Formal Claim

This claim covers a fresh same-Project attempt. The run journal provides
evidence for continuations.

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
                'candidate_image_prepared': {'target': 'checking_image_suite', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
                'build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'checking_image_suite': {'on': {
                'image_suite_passed': {'target': 'checking_mcp_canary', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
                'image_suite_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'checking_mcp_canary': {'on': {
                'mcp_canary_passed': {'target': 'installing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed'}}},
                'mcp_canary_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
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
