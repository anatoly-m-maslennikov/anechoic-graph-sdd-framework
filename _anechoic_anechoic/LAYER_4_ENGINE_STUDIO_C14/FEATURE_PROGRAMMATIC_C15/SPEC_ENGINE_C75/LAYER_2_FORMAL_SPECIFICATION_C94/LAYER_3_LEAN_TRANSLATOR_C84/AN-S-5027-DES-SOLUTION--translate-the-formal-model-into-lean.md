---
atom_family: SPEC
atom_id: AN-S-5027
container:
  component: C84
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4931@1
state:
  status: active
  version: 1
  updated_at: '2026-11-27T00:00:00Z'
---

## Summary

Translate the formal model into Lean.


## Claim

### Prose Claim

Call C85 to normalize the pinned declarations. Encode each admitted
declaration and its source in Lean. Add the executable shape or framing
declaration, then return Lean source with the normalized result.


### Formal Claim

```python
component_workflow(
    component='C84',
    action='compile_lean',
    machine={
        'id': 'c84_compile_lean',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'requested': {'target': 'working', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'trigger'}}},
            }},
            'working': {'on': {
                'effect_recorded': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C84.lean_source', 'outcome': 'generated',
                               'detail': {'model': 'request_normalized_model'}}}},
            }},
            'returning': {'on': {
                'result_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'compiled'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

Run Lean on the supplied program. Decode its output as JSON. Return the value,
or raise `ValueError` when execution or JSON decoding fails.

```python
component_workflow(
    component='C84', action='run_lean_json',
    machine={'id': 'run_lean_json', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'running', 'expect': {
            'kind': 'trigger', 'target': 'run_lean_json',
            'detail': {'transport': 'in_process', 'entry': '_package__shared.run_lean_json'}}}}},
        'running': {'on': {
            'evaluated': {'to': 'returning', 'expect': {
                'kind': 'effect', 'target': 'C84.lean_evaluation', 'outcome': 'returned'}},
            'error': {'to': 'raising', 'expect': {
                'kind': 'effect', 'target': 'C84.lean_evaluation', 'outcome': 'failed'}},
        }},
        'returning': {'on': {'returned': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'fulfilled'}}}},
        'raising': {'on': {'raised': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'failed'}}}},
        'done': {'type': 'final'},
    }},
)
```
