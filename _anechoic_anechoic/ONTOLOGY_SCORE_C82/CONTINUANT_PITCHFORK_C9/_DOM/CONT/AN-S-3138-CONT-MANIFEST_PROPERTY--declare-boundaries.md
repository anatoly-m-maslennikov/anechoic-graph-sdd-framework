---
atom_family: SPEC
atom_id: AN-S-3138
concern:
  subject: Boundaries
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:32.729755+00:00"
---

## Summary

Declare Boundaries

## Semantics

The `boundaries` value can contain optional top-level `code`, `process`, `state`, and `io` sections. `boundaries.code.imports` defines the caller scope for Code Access. Optional `boundaries.process` records execution owner, launch, and lifetime only when established; no process field is required. `boundaries.state` keeps existing state semantics. `boundaries.io` defines served and used interfaces.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3138(Property):
    name = 'Boundaries'
    bearer = ComponentManifest
    field_options = {'default': None}
    property.value.format = dict[str, object] | None
```
