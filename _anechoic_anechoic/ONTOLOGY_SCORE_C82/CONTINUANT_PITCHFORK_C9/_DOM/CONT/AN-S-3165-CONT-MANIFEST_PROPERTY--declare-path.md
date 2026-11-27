---
atom_family: SPEC
atom_id: AN-S-3165
concern:
  subject: Path
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Concern
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 7
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare Path

## Semantics

Concern Path Notation uses operators as shorthand for relations, Properties, and value selections. A Concern Path is an expression in this notation that locates a Model or Project entity.

- `/` follows containment from container to member.
- `//` follows specialization from the broader kind to the narrower kind.
- `.` selects a Property.
- `:=` selects an allowed Property value.
- `()` groups a qualifier.
- `>|` follows an Axis or Axis value from an entity.
- `|<` follows an Axis or Axis value toward the entity.

```text
atom.state.status >| status group := current
status group := current |< atom.state.status
```

For a template-defined variant, keep the specialization step in the Path. For example, use `Atom//Spec Atom//.Header.Context` as the Path, `.` as the Relation, and `Template := axiom` as the Subject. Group the selection to append further steps.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3165(Property):
    name = 'Path'
    bearer = Atom.Header.Concern
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 1
    property.value.format = str | None
```
