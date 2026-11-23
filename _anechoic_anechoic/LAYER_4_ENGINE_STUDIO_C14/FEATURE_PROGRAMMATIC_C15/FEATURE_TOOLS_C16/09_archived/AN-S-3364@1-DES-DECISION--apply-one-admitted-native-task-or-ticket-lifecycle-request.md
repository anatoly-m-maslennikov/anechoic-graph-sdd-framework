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
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@1
  IS_SOLUTION_FOR:
  - AN-S-3304@2
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Apply one admitted native Task or Ticket lifecycle request.

## Claim

### Prose Claim

The CLI checks the pinned Project and captures carriers, then dispatches
the lifecycle operation. Report its result, including any effects. A
rejected request or runtime error can exit on stderr.

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
                    {'kind': 'trigger'}}},
            }},
            'checking': {'on': {
                'pinned_carriers_captured': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C16', 'outcome': 'succeeded'}}},
                'request_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'executing': {'on': {
                'lifecycle_operation_dispatched': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C16'}}},
                'lifecycle_error': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'lifecycle_result': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output'}}},
                'lifecycle_error': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reported': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
