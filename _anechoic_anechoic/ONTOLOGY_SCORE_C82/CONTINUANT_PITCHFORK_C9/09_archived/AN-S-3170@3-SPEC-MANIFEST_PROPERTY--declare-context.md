---
atom_family: SPEC
atom_id: AN-S-3170
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.478753+00:00'
---

## Summary

Declare Context

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Context

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3170(Property):
    name = 'Context'
    bearer = Atom.Header
    allowed_dependent_property_names = ('Template', 'Label', 'Lens')
    ordered_dependent_property_pairs = (('Template', 'Label'), ('Label', 'Lens'))
    property_occurrence_cardinality = Cardinality(minimum=0, maximum=1)
    value_cardinality = 0
    value_format = object
```
