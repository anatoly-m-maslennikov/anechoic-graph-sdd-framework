---
atom_family: SPEC
atom_id: AN-S-5028
container:
  component: C87
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4934@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T00:00:00Z'
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
                                                                         'outcome': 'rendered',
                                                                         'detail': {'model': 'request_normalized_model'}}}}}},
            'done': {'type': 'final'},
            'return_rendered': {'on': {'rendered_returned': {'target': 'done',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'output',
                                                                                  'outcome': 'rendered'}}}}}}},
)
```
