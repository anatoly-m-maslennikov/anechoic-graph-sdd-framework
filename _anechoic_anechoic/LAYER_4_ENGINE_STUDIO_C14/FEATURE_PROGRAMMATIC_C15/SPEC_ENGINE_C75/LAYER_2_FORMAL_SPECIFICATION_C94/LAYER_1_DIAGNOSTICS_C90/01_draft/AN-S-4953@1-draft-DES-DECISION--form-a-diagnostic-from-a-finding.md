---
atom_family: SPEC
atom_id: AN-S-4953
container:
  component: C90
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4952@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
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
                    'params': {'kind': 'trigger'}}},
            }},
            'working': {'on': {
                'effect_recorded': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C90.source_diagnostic', 'outcome': 'formed'}}},
            }},
            'returning': {'on': {
                'result_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'reported'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
