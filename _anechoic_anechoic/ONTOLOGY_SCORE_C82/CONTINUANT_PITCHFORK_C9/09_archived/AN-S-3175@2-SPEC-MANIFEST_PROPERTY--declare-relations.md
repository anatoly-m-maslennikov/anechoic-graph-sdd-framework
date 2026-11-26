---
atom_family: SPEC
atom_id: AN-S-3175
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.490261+00:00'
---

## Summary

Declare Relations

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Relations

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3175(Property):
    name = 'Relations'
    bearer = Atom.Header
    dependent_property_cardinality = Cardinality(minimum=1, maximum=None)
    dependent_property_value_cardinality = Cardinality(minimum=1, maximum=None)
    dependent_property_value_format = str
    field_options = {'default': None, 'kw_only': True}
    property_occurrence_cardinality = Cardinality(minimum=0, maximum=1)
    value_cardinality = 0
    value_format = dict[str, list[str]] | None
```
