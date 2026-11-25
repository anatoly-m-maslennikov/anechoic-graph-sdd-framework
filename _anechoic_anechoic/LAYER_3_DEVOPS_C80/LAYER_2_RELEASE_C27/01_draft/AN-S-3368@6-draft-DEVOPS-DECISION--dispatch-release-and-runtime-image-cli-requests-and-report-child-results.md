---
atom_family: SPEC
atom_id: AN-S-3368
container:
  component: C27
tier: 1
context:
  template: DECISION
  lens: DevOps
relations:
  IS_SOLUTION_FOR:
  - AN-S-3288@15-draft
state:
  status: draft
  version: 6
  updated_at: '2026-11-25T10:24:04.712334+00:00'
---

## Summary

Dispatch release and runtime image CLI requests and report child results.

## Claim

### Prose Claim

The release CLI dispatches the selected command to its child, then reports
its JSON result and exit status. `prepare-local` dispatches to C63. Help lists the commands and exits 0. Invalid
CLI usage exits 2. Interruption exits 130. Exit 1 means another reported outcome.

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
                'run_image_selected': {'target': 'dispatching_run_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'run-image'}}}},
            }},
            'dispatching_local': {'on': {
                'local_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
            }},
            'dispatching_prepare_local': {'on': {
                'prepare_local_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
            }},
            'dispatching_public': {'on': {
                'public_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C64'}}},
            }},
            'dispatching_build_image': {'on': {
                'build_image_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81'}}},
            }},
            'dispatching_run_image': {'on': {
                'run_image_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81'}}},
            }},
            'responding': {'on': {
                'child_result_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```
