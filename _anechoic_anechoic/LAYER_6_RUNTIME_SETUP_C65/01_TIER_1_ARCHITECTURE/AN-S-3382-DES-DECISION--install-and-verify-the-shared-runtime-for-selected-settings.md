---
atom_family: SPEC
atom_id: AN-S-3382
container:
  component: C65
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@1
  IS_SOLUTION_FOR:
  - AN-S-3297@5
state:
  status: active
  version: 1
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Install and verify the shared runtime for selected settings.

## Claim

### Prose Claim

Setup selects settings, checks prerequisites, optionally initializes a
project, builds an image, starts and verifies MCP, and may install Codex
integration.

### Formal Claim

```python
component_workflow(
    component='C65',
    action='install_shared_runtime',
    machine={
        'id': 'c65_install_shared_runtime',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'install_requested': {'target': 'preparing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'preparing': {'on': {
                'settings_and_project_prepared': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65'}}},
                'preparation_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'install_interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted'}}},
            }},
            'building': {'on': {
                'image_built': {'target': 'launching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'completed'}}},
                'image_build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'install_interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted'}}},
            }},
            'launching': {'on': {
                'runtime_verified': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21', 'outcome': 'ready'}}},
                'runtime_launch_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'install_interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted'}}},
            }},
            'reporting': {'on': {
                'install_result_completed': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed'}}},
                'codex_install_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'install_interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted'}}},
            }},
            'completed': {'type': 'final'},
            'failed': {'type': 'final'},
            'interrupted': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
