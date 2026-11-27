---
atom_family: SPEC
atom_id: AN-S-3145
concern:
  subject: Boundaries
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:32.992129+00:00"
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
