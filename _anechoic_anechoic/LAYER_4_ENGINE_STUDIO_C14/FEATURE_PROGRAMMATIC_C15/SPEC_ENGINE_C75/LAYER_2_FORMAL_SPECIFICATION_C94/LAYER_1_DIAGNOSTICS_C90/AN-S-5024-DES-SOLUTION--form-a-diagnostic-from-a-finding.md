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
  - AN-S-4937@2
state:
  status: active
  version: 2
  updated_at: "2026-11-27T05:39:19.358055+00:00"
---

## Summary

Form a diagnostic from a finding.

## Approach

Take the finding source, field, and message. Form a diagnostic that retains each value.

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
