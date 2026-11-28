---
atom_family: SPEC
atom_id: AN-S-3380
container:
  component: C63
tier: 0
context:
  template: solution
  lens: DevOps
relations:
  ANSWERS:
  - AN-S-3290@19-draft
state:
  status: draft
  version: 10
  updated_at: '2026-11-28T10:13:43.794431+00:00'
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
passing phase whose inputs and evidence still match. The delivery claim
pins the accepted revision and exact artifact. Reconcile the artifact before
repeating an effect. After verified promotion, resume only pending cleanup.

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
                    {'kind': 'trigger', 'target': 'local_release', 'detail': {'transport': 'cli', 'runner': 'uv', 'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py', 'command': 'local'}}}},
            }},
            'preparing': {'on': {
                'inputs_validated_and_version_bumped': {'target': 'testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
                'preparation_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'testing': {'on': {
                'static_passed': {'target': 'functional_testing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'static tests', 'outcome': 'passed'}}},
                'tests_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'functional_testing': {'on': {
                'functional_passed': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'functional tests', 'outcome': 'passed'}}},
                'tests_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'building': {'on': {
                'candidate_image_prepared': {'target': 'checking_image_suite', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'prepare candidate image', 'outcome': 'completed'}}},
                'build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'checking_image_suite': {'on': {
                'image_suite_passed': {'target': 'checking_mcp_canary', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'verify candidate image', 'outcome': 'passed'}}},
                'image_suite_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'checking_mcp_canary': {'on': {
                'mcp_canary_passed': {'target': 'installing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'verify candidate canary', 'outcome': 'passed'}}},
                'mcp_canary_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'installing': {'on': {
                'package_installed': {'target': 'starting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'copy product to installed framework', 'outcome': 'completed'}}},
                'installation_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'starting': {'on': {
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
