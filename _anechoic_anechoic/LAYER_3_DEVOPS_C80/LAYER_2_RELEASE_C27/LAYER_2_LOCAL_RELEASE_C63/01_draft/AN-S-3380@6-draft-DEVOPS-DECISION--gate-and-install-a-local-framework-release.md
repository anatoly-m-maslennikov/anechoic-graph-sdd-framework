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
  IS_SOLUTION_FOR:
  - AN-S-3292@10-draft
state:
  status: draft
  version: 6
  updated_at: '2026-11-25T09:38:50.838724+00:00'
---

## Summary

Gate and install a local Framework release.

## Claim

### Prose Claim

Validate the inputs and report completion or failure with evidence. C81 builds
the candidate from the selected checkout through `build_project_image` and
returns the image. C63 verifies and installs that image. C81 launches the Project
runtime through `start_project_runtime` with that image and the Project Manifest
port, and returns a health-checked MCP endpoint. C21 performs the shared MCP
container start.

### Formal Claim

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
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed', 'detail': {'release_stage': 'static'}}}},
                'tests_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'functional_testing': {'on': {
                'host_functional_tests_passed': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed', 'detail': {'release_stage': 'functional'}}}},
                'tests_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'building': {'on': {
                'candidate_image_prepared': {'target': 'awaiting_candidate_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81', 'outcome': 'succeeded', 'detail': {'release_stage': 'build', 'image_ref': 'release_candidate'}}}},
                'build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'awaiting_candidate_image': {'on': {
                'candidate_image_returned': {'target': 'verifying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81.image', 'outcome': 'built', 'detail': {'component': 'C81', 'action': 'build_project_image', 'output': 'succeeded'}}}},
                'build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'verifying': {'on': {
                'candidate_image_verified': {'target': 'installing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C19', 'outcome': 'passed', 'detail': {'release_stage': 'verify_image', 'image_ref': 'release_candidate'}}}},
                'verification_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'installing': {'on': {
                'candidate_installed': {'target': 'starting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63', 'outcome': 'succeeded', 'detail': {'release_stage': 'install', 'image_ref': 'release_candidate'}}}},
                'installation_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'starting': {'on': {
                'project_runtime_started': {'target': 'awaiting_healthy_endpoint', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81', 'outcome': 'succeeded', 'detail': {'release_stage': 'start', 'image_ref': 'release_candidate'}}}},
                'runtime_start_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'awaiting_healthy_endpoint': {'on': {
                'healthy_endpoint_received': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81.mcp_endpoint', 'outcome': 'healthy', 'detail': {'component': 'C81', 'action': 'start_project_runtime', 'output': 'succeeded'}}}},
                'runtime_start_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
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
