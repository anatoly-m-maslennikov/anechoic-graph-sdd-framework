---
atom_family: SPEC
atom_id: AN-S-4959
container:
  component: C87
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4958@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Render a Mermaid Solution diagram.

## Claim

### Prose Claim

Select the renderer for the admitted Solution claim, render its diagram, and return the rendered outcome.

### Formal Claim

```python
component_workflow(
    component='C87',
    action='render_solution',
    machine={'id': 'c87_render_solution',
 'initial': 'idle',
 'states': {'idle': {'on': {'requested': {'target': 'checking',
                                          'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'checking': {'on': {'rendered_effect': {'target': 'return_rendered',
                                                    'guard': {'type': 'matchesTrace',
                                                              'params': {'kind': 'effect',
                                                                         'target': 'C87.mermaid_diagram',
                                                                         'outcome': 'rendered'}}}}},
            'done': {'type': 'final'},
            'return_rendered': {'on': {'rendered_returned': {'target': 'done',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'output',
                                                                                  'outcome': 'rendered'}}}}}}},
)
```
