---
atom_family: SPEC
atom_id: AN-S-3368
container:
  component: C27
tier: 0
context:
  template: solution
  lens: DevOps
relations:
  ANSWERS:
  - AN-S-3038@10-draft
state:
  status: draft
  version: 10
  updated_at: '2026-11-25T10:24:04.712334+00:00'
---

## Summary

Dispatch release CLI requests and report child results.

## Claim

The workflow shows the first child call for each standard command. The
`local` command also supports snapshot and maintenance modes. Those modes
select other C63 entry points and require separate checks.

### Formal Claim

```python
component_workflow(
    component='C27',
    action='dispatch_framework_release',
    machine={
        'id': 'c27_dispatch_framework_release',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'release_request_received': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'release', 'detail': {'transport': 'cli', 'runner': 'uv', 'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py'}}}},
            }},
            'selecting': {'on': {
                'local_selected': {'target': 'dispatching_local', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'local'}}}},
                'prepare_local_selected': {'target': 'dispatching_prepare_local', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'prepare-local'}}}},
                'public_selected': {'target': 'dispatching_public', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'public'}}}},
                'build_image_selected': {'target': 'dispatching_build_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'build-image'}}}},
                'verify_image_selected': {'target': 'dispatching_verify_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'verify-image'}}}},
                'run_image_selected': {'target': 'dispatching_run_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'run-image'}}}},
            }},
            'dispatching_local': {'on': {
                'local_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63', 'detail': {
                        'manifest': 'AN-S-3290@15-draft', 'action': 'run_local_release',
                        'entry': 'run_local_release',
                    }}}},
            }},
            'dispatching_prepare_local': {'on': {
                'prepare_local_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63', 'detail': {
                        'manifest': 'AN-S-3290@15-draft', 'action': 'prepare_local',
                        'entry': 'prepare_local',
                    }}}},
            }},
            'dispatching_public': {'on': {
                'public_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C64', 'detail': {
                        'manifest': 'AN-S-3291@8-draft', 'action': 'prepare_public_release',
                        'entry': 'run_public_release',
                    }}}},
            }},
            'dispatching_build_image': {'on': {
                'build_image_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81', 'detail': {
                        'manifest': 'AN-S-4704@5-draft', 'action': 'build_and_run_runtime_images',
                        'entry': 'build_image',
                    }}}},
            }},
            'dispatching_verify_image': {'on': {
                'verify_image_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63', 'detail': {
                        'manifest': 'AN-S-3290@15-draft', 'action': 'verify_image',
                        'entry': 'verify_image',
                    }}}},
            }},
            'dispatching_run_image': {'on': {
                'run_image_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81', 'detail': {
                        'manifest': 'AN-S-4704@5-draft', 'action': 'build_and_run_runtime_images',
                        'entry': 'launch_shared_image', 'apply_flag': '--apply',
                    }}}},
            }},
            'responding': {'on': {
                'completion_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed', 'detail': {'exit_code': 0, 'stdout': 'json_object'}}}},
                'incomplete_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'incomplete', 'detail': {'exit_code': 1, 'stdout': 'json_object'}}}},
                'interruption_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130, 'stdout': 'json_object', 'error_type': 'KeyboardInterrupt'}}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```
