---
atom_family: SPEC
atom_id: AN-S-4957
container:
  component: C84
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4956@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Translate the formal model into Lean.

## Approach

Call C85 to normalize the pinned declarations. Encode each admitted
declaration and its source in Lean. Add the executable shape or framing
declaration, then return Lean source with the normalized result.

## Claim

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
