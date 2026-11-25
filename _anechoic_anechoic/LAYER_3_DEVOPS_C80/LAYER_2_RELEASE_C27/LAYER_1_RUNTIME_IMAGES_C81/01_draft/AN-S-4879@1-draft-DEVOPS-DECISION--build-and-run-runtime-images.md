---
atom_family: SPEC
atom_id: AN-S-4879
container:
  component: C81
tier: 1
context:
  template: DECISION
  lens: DevOps
relations:
  IS_SOLUTION_FOR:
  - AN-S-4732@2-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Build and run runtime images.

## Claim

### Prose Claim

Build returns the immutable image ID, input fingerprint, and version without
release or installation. Run uses the selected exact image and host settings.
Without `--apply`, it returns the plan without container changes. The CLI reports wire outcome `completed` for dry-run; the logical outcome is `launch_planned`. With `--apply`,
it waits for readiness; `--verify-mcp` adds an MCP probe before success.
Record the image result before reporting it.

For Local Release, the same build owner receives the selected checkout and
returns its immutable image. Start uses the selected Project, the exact selected
image, and the supplied loopback port. It returns the health-checked MCP endpoint.
C81 uses `start_container` to launch Docker directly for this Project runtime. The separate shared-image apply path calls C21. These logical calls do not select a CLI or API transport.

### Formal Claim

```python
component_workflow(
    component='C81',
    action='build_and_run_runtime_images',
    machine={
        'id': 'c81_build_and_run_runtime_images',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'request_received': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'runtime_images', 'detail': {'transport': 'cli', 'runner': 'uv', 'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py'}}}},
            }},
            'selecting': {'on': {
                'build_selected': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'build-image'}}}},
                'run_selected': {'target': 'planning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'command': 'run-image'}}}},
            }},
            'building': {'on': {
                'image_built': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81', 'outcome': 'image_built'}}},
            }},
            'planning': {'on': {
                'plan_prepared': {'target': 'deciding_apply', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81', 'outcome': 'launch_plan_prepared'}}},
            }},
            'deciding_apply': {'on': {
                'plan_only': {'target': 'reporting_plan', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'apply': False}}}},
                'apply': {'target': 'awaiting_applied_launch', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'apply': True}}}},
            }},
            'awaiting_applied_launch': {'on': {
                'runtime_ready': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'apply_shared_runtime_launch', 'outcome': 'runtime_ready', 'detail': {'apply': True, 'verify_mcp': False}}}},
                'mcp_verified': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'apply_shared_runtime_launch', 'outcome': 'mcp_verified', 'detail': {'apply': True, 'verify_mcp': True}}}},
            }},
            'reporting_plan': {'on': {
                'plan_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'launch_planned'}}},
            }},
            'reporting': {'on': {
                'image_result_recorded': {'target': 'returning_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81.image_result', 'outcome': 'reported'}}},
            }},
            'returning_result': {'on': {
                'result_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'image_result_reported'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C81', action='apply_shared_runtime_launch',
    machine={
        'id': 'c81_apply_shared_runtime_launch', 'initial': 'idle',
        'states': {
            'idle': {'on': {
                'apply_requested': {'target': 'selecting_apply', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'runtime_images', 'detail': {'command': 'run-image', 'apply': True}}}},
            }},
            'selecting_apply': {'on': {
                'apply_selected': {'target': 'launching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'shared_runtime_launch', 'outcome': 'apply_selected'}}},
            }},
            'launching': {'on': {
                'launch_requested': {'target': 'waiting_for_readiness', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21', 'outcome': 'launch_requested'}}},
            }},
            'waiting_for_readiness': {'on': {
                'ready': {'target': 'deciding_probe', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21', 'outcome': 'ready'}}},
            }},
            'deciding_probe': {'on': {
                'probe_skipped': {'target': 'reporting_ready', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'verify_mcp': False}}}},
                'probe_selected': {'target': 'requesting_probe', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'detail': {'verify_mcp': True}}}},
            }},
            'requesting_probe': {'on': {
                'probe_requested': {'target': 'probing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'shared_runtime_mcp_probe', 'outcome': 'requested'}}},
            }},
            'probing': {'on': {
                'probe_verified': {'target': 'reporting_verified', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'shared_runtime_mcp', 'outcome': 'verified'}}},
            }},
            'reporting_ready': {'on': {
                'runtime_ready': {'target': 'ready_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'runtime_ready'}}},
            }},
            'reporting_verified': {'on': {
                'mcp_verified': {'target': 'verified_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'mcp_verified'}}},
            }},
            'ready_result': {'type': 'final'}, 'verified_result': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C81',
    action='build_project_image',
    machine={
        'id': 'c81_build_project_image',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'request_received': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'build_project_image'}}},
            }},
            'building': {'on': {
                'image_built': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81.image', 'outcome': 'built'}}},
            }},
            'returning': {'on': {
                'image_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C81',
    action='start_project_runtime',
    machine={
        'id': 'c81_start_project_runtime',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'request_received': {'target': 'launching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'start_project_runtime'}}},
            }},
            'launching': {'on': {
                'launch_requested': {'target': 'checking_health', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81.project_container', 'outcome': 'launch_requested'}}},
            }},
            'checking_health': {'on': {
                'endpoint_health_checked': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C81.mcp_endpoint', 'outcome': 'healthy'}}},
            }},
            'returning': {'on': {
                'endpoint_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
