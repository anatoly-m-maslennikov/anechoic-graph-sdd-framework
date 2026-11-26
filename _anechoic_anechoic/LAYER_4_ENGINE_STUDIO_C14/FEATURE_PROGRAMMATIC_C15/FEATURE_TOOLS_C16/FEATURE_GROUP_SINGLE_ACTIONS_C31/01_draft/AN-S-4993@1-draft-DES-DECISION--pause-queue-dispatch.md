---
atom_family: SPEC
atom_id: AN-S-4993
container:
  component: C40
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4992@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00+00:00'
---

## Summary

Pause queue dispatch.

## Claim

### Prose Claim

Pause dispatch through the direct queue-control path. This path is not queued on a paused queue. Pausing does not cancel running work.

The successful pause reports dispatch as paused and does not cancel running work. Queue selection, inputs, failure behavior and other effects remain open.

### Formal Claim

```python
component_workflow(
    component='C40', action='pause_queue_dispatch',
    machine={
        'id': 'c40_pause_queue_dispatch', 'initial': 'idle',
        'states': {
            'idle': {'on': {'request': {'target': 'working', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'working': {'on': {'effect_0': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'dispatch', 'outcome': 'paused'}}}}},
            'returning': {'on': {'return': {'target': 'returned', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'dispatch_paused'}}}}},
            'returned': {'type': 'final'},
        },
    },
)
```

## Details

The trace models only the named successful outcome. It does not prove the input, failure rules, or unmodeled effects.
