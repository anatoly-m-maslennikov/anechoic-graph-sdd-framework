---
atom_family: SPEC
atom_id: AN-S-3145
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T15:54:02.338459+00:00"
---

## Summary

Declare Boundaries

## Semantics

Use the Component Manifest Boundary semantics for this mapping. `boundaries.code.imports` defines the caller scope for Code Access, and optional `boundaries.process`, `boundaries.state`, and `boundaries.io` carry process metadata, existing state semantics, and served and used interfaces.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentSeedManifest, Property

class Property3145(Property):
    name = 'Boundaries'
    bearer = ComponentSeedManifest
    field_options = {'default': None}
    property.value.format = dict[str, object] | None
```
