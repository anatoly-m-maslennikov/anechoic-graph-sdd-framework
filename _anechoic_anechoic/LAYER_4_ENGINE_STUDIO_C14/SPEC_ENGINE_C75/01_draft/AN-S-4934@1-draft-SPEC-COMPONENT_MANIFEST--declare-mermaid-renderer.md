---
atom_family: SPEC
atom_id: AN-S-4934
container:
  component: C75
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Mermaid Renderer

## Purpose

Render a Mermaid Solution diagram from the normalized formal model.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C87',
        layer=3,
        name='Mermaid Renderer',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {'server': {'render_solution': {'outcomes': {
                'rendered': {'must_effect': [('C87.mermaid_diagram', 'rendered')]},
            }}}},
        },
    ),
)
```
