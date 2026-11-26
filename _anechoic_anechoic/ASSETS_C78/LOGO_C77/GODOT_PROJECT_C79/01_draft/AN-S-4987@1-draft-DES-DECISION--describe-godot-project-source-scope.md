---
atom_family: SPEC
atom_id: AN-S-4987
container:
  component: C79
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4986@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Describe Godot Project source scope

## Claim

### Prose Claim

The project source tree contains `project.godot`, `studio.tscn`, scripts, plots, and market assets. Its README describes the editable scene and source assets.

The model records this source boundary. Its transitions do not claim execution or runtime effects.

### Formal Claim

```python
component_workflow(
    component='C79',
    action='describe_godot_project_scope',
    machine={
        'id': 'c79_describe_godot_project_scope',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'scope_requested': {'target': 'scope', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'scope': {'on': {
                'resource_recorded': {'target': 'result', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'godot_project.editable_sources', 'outcome': 'present'}}},
            }},
            'result': {'on': {
                'scope_described': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'godot_project_scope_described'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
