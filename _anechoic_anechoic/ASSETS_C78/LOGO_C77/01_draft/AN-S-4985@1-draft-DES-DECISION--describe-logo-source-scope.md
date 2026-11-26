---
atom_family: SPEC
atom_id: AN-S-4985
container:
  component: C77
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4984@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Describe Logo source scope

## Claim

### Prose Claim

The Logo source tree contains `anechoic_logo_day.png`, `anechoic_logo_day_art.png`, and `GODOT_PROJECT_C79`. C79 is declared by AN-S-4494.

The model records this source boundary. Its transitions do not claim execution or runtime effects.

### Formal Claim

```python
component_workflow(
    component='C77',
    action='describe_logo_scope',
    machine={
        'id': 'c77_describe_logo_scope',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'scope_requested': {'target': 'scope', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'scope': {'on': {
                'resource_recorded': {'target': 'result', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'logo.godot_project', 'outcome': 'declared'}}},
            }},
            'result': {'on': {
                'scope_described': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'logo_scope_described'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
