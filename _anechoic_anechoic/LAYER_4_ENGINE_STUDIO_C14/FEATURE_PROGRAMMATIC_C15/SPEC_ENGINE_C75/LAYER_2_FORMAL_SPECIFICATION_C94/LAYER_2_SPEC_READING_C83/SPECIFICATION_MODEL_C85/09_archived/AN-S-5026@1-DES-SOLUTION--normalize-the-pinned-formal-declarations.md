---
atom_family: SPEC
atom_id: AN-S-5026
container:
  component: C85
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4932@1
state:
  status: archived
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Normalize the pinned formal declarations.

## Approach

Validate the Manifest. Parse each supported claim for its carrier role and Component. Collect normalized declarations and source-linked issues or unresolved findings.

## Claim

### Formal Claim

```python
component_workflow(
    component='C85',
    action='normalize_spec',
    machine={
        'id': 'c85_normalize_spec',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'requested': {'target': 'working', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'trigger'}}},
            }},
            'working': {'on': {
                'effect_recorded': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C85.formal_declarations', 'outcome': 'normalized',
                               'detail': {'model': 'request_normalized_model'}}}},
            }},
            'returning': {'on': {
                'result_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'normalized'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
