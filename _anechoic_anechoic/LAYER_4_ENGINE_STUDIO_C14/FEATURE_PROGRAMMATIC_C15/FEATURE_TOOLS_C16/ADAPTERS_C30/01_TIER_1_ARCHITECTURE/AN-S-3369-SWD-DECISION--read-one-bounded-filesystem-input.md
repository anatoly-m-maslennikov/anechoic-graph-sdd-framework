---
atom_family: SPEC
atom_id: AN-S-3369
container:
  component: C30
tier: 1
context:
  template: DECISION
  lens: SWD
relations:
  IS_SOLUTION_FOR:
  - AN-S-3303@15
state:
  status: active
  version: 2
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---

## Summary

Read one bounded filesystem input.

## Claim

### Prose Claim

The guarded reader checks roots, protected paths, symlinks, file type and
limits, then records a fingerprint and returns bytes.

### Formal Claim

```python
component_workflow(
    component='C30',
    action='read_guarded_input',
    machine={
        'id': 'c30_read_guarded_input',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'bounded_read_requested': {'target': 'checking', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'checking': {'on': {
                'input_opened_and_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C30', 'outcome': 'succeeded'}}},
                'read_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'bytes_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
