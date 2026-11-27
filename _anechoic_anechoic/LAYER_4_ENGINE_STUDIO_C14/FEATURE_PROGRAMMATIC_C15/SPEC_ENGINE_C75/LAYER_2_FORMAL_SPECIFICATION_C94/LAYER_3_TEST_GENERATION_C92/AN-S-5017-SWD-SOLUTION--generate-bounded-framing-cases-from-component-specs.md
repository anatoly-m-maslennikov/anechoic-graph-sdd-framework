---
atom_family: SPEC
atom_id: AN-S-5017
container:
  component: C92
tier: 0
context:
  template: solution
  lens: SWD
relations:
  ANSWERS: [AN-S-5016@1]
state:
  status: active
  version: 1
  updated_at: '2026-11-26T20:51:22.387413+00:00'
---
## Summary

Generate bounded framing cases from Component Specs

## Claim

Read the normalized framing claims. Form inputs from both declarations
and evaluate each declaration on each input. Attach the declared operations,
source pins, and unresolved obligations to the result.

### Formal Claim

```python
component_workflow(
    component='C92',
    action='generate_framing_cases',
    machine={
        'id': 'generate_framing_cases',
        'initial': 'idle',
        'states': {
            'idle': {'on': {'request': {'to': 'derive', 'expect': {
                'kind': 'trigger', 'target': 'framing_cases',
                'detail': {'transport': 'in_process',
                           'entry': '_package__shared.build_python_framing_cases'},
            }}}},
            'derive': {'on': {'cases': {'to': 'reply', 'expect': {
                'kind': 'effect', 'target': 'test_cases', 'outcome': 'derived',
            }}}},
            'reply': {'on': {'return_cases': {'to': 'done', 'expect': {
                'kind': 'output', 'outcome': 'generated',
            }}}},
            'done': {'type': 'final'},
        },
    },
)
```
