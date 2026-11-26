---
atom_family: SPEC
atom_id: AN-S-3364
container:
  component: C16
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3304@3-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:00:30.737290+00:00'
---

## Summary

Apply one admitted native Task or Ticket lifecycle request.

## Claim

### Prose Claim

The CLI checks the pinned Project and captures carriers, then dispatches
the lifecycle operation. A rejected request or runtime error can exit on
stderr.

### Formal Claim

```python
component_workflow(
    component='C16',
    action='apply_native_lifecycle',
    machine={
        'id': 'c16_apply_native_lifecycle',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'lifecycle_request': {'target': 'checking', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'task_lifecycle', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'module': 'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli',
                        'stdin': ('bound Task, Epic, or Ticket Asset lifecycle request and '
                                  'Model and Structure attestation on stdin'),
                    }}}},
            }},
            'checking': {'on': {
                'pinned_carriers_captured': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C16', 'outcome': 'succeeded'}}},
                'request_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'preflight_rejected'}}},
            }},
            'executing': {'on': {
                'lifecycle_operation_dispatched': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'lifecycle_dispatch', 'outcome': 'dispatched'}}},
                'lifecycle_error': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'native_lifecycle_failure', 'outcome': 'reported'}}},
            }},
            'responding': {'on': {
                'lifecycle_result': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {
                        'output_fields': ['outcome', 'file_effects'],
                        'stdout': 'native outcome and file effects on stdout',
                    }}}},
                'lifecycle_error': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'native_lifecycle_failure', 'outcome': 'reported'}}},
            }},
            'reporting_error': {'on': {
                'lifecycle_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reported': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```
