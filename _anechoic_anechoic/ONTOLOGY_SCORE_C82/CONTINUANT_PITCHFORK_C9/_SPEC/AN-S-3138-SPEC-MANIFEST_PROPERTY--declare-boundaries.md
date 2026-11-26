---
atom_family: SPEC
atom_id: AN-S-3138
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T16:00:37.905829+00:00"
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
