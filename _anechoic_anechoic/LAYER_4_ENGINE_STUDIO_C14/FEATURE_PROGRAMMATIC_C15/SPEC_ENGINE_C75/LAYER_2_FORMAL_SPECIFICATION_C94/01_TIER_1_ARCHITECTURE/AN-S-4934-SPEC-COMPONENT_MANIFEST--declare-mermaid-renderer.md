---
atom_family: SPEC
atom_id: AN-S-4934
container:
  component: C94
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Mermaid Renderer

## Purpose

Render a Mermaid Solution diagram from the normalized formal model.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(component_id='C87', layer=3, name='Mermaid Renderer', lens_whitelist=['DES', 'SPEC']),
)
```

## Component Boundaries

```python
{'code': {'exports': {'_package__shared.framing_to_mermaid': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.group_to_mermaid': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.render_solution': {'shared': ['C75',
                                                                      'C88',
                                                                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.render_workflow_diagram': {'shared': ['C75',
                                                                              'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']}}},
 'io': {'server': {'render_solution': {'outcomes': {'rendered': {'must_effect': [('C87.mermaid_diagram',
                                                                                  'rendered',
                                                                                  {'model': 'request_normalized_model'})]}}}}}}
```

## Component Contract

Render a Mermaid diagram for the admitted Solution claim from the normalized formal model. The diagram represents the selected supported claim form.


```python trace
declare_trace_contract(
    action='render_solution',
    output='rendered',
    must_effect=(('C87.mermaid_diagram', 'rendered', {'model': 'request_normalized_model'}),),
)
```
