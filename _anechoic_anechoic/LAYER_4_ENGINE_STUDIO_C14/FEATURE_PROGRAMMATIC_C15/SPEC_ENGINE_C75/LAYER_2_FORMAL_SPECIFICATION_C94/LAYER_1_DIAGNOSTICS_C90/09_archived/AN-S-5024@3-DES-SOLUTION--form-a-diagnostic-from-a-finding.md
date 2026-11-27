---
atom_family: SPEC
atom_id: AN-S-5024
container:
  component: C90
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4937@3
state:
  status: archived
  version: 3
  updated_at: '2026-11-27T11:37:27.939414+00:00'
---

## Summary

Form a diagnostic from a finding.

## Approach

Take the finding source, field, and message. Form a diagnostic that retains each value.

For verdict aggregation, check for `conflicting` first. If it is absent,
check for an empty list or `unresolved`. Return `matched` when both
checks are false.

## Claim

### Formal Claim

```python
component_workflow(
    component='C90',
    action='finding',
    machine={
        'id': 'c90_finding',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'requested': {'target': 'working', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'trigger',
                               'bind': {'source': 'source', 'field': 'field', 'message': 'message'}}}},
            }},
            'working': {'on': {
                'effect_recorded': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C90.source_diagnostic', 'outcome': 'formed'}}},
            }},
            'returning': {'on': {
                'result_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'reported',
                               'same_as': {'source': 'source', 'field': 'field', 'message': 'message'}}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
