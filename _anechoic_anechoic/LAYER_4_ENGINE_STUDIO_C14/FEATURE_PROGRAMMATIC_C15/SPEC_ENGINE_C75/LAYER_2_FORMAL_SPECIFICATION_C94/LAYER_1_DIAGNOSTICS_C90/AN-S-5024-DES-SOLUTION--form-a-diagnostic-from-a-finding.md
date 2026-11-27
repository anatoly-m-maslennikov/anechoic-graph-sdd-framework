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
  - AN-S-4937@4
state:
  status: active
  version: 4
  updated_at: '2026-11-27T12:22:53.034284+00:00'
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

```python
component_workflow(
    component='C90',
    action='verdict',
    machine={
        'id': 'c90_verdict',
        'initial': 'classify',
        'states': {
            'classify': {'on': {
                'conflicting': {'to': 'return_conflicting', 'expect': {
                    'kind': 'effect', 'target': 'C90.verdict_input',
                    'outcome': 'observed',
                    'detail': {'has_conflict': True},
                }},
                'unresolved': {'to': 'return_unresolved', 'expect': {
                    'kind': 'effect', 'target': 'C90.verdict_input',
                    'outcome': 'observed',
                    'detail': {'has_conflict': False, 'unresolved_or_empty': True},
                }},
                'matched': {'to': 'return_matched', 'expect': {
                    'kind': 'effect', 'target': 'C90.verdict_input',
                    'outcome': 'observed',
                    'detail': {'has_conflict': False, 'unresolved_or_empty': False},
                }},
            }},
            'return_conflicting': {'on': {'result': {'to': 'done',
                'expect': {'kind': 'output', 'outcome': 'conflicting'}
            }}},
            'return_unresolved': {'on': {'result': {'to': 'done',
                'expect': {'kind': 'output', 'outcome': 'unresolved'}
            }}},
            'return_matched': {'on': {'result': {'to': 'done',
                'expect': {'kind': 'output', 'outcome': 'matched'}
            }}},
            'done': {'type': 'final'},
        },
    },
)
```
