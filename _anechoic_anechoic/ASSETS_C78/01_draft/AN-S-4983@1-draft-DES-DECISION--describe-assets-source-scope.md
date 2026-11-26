---
atom_family: SPEC
atom_id: AN-S-4983
container:
  component: C78
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4982@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Describe Assets source scope

## Claim

### Prose Claim

The Assets source tree contains `ASSETS_C78/LOGO_C77`; C77 is declared by AN-S-3398.

The model records this source boundary. Its transitions do not claim execution or runtime effects.

### Formal Claim

```python
component_workflow(
    component='C78',
    action='describe_assets_scope',
    machine={
        'id': 'c78_describe_assets_scope',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'scope_requested': {'target': 'scope', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'scope': {'on': {
                'resource_recorded': {'target': 'result', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'assets.logo', 'outcome': 'declared'}}},
            }},
            'result': {'on': {
                'scope_described': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'assets_scope_described'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
