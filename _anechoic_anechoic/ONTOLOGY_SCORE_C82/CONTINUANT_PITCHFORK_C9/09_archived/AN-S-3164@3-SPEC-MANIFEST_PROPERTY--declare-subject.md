---
atom_family: SPEC
atom_id: AN-S-3164
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.466639+00:00'
---

## Summary

Declare Subject

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Concern.Subject

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3164(Property):
    name = 'Subject'
    bearer = Atom.Header.Concern
    field_options = {'default': None, 'kw_only': True}
    property_occurrence_cardinality = Cardinality(minimum=0, maximum=1)
    value_cardinality = 1
    value_format = str | None
```
