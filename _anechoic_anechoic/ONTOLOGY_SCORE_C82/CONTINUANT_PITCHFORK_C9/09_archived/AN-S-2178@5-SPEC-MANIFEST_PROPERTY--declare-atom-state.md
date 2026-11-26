---
atom_family: SPEC
atom_id: AN-S-2178
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: '2026-11-24T16:58:01.305622+00:00'
---


## Summary

Declare Atom.State

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.State

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2178(Property):
    name = 'State'
    bearer = Atom.Header
    allowed_dependent_property_names = ('Status', 'Version', 'Updated At')
    ordered_dependent_property_pairs = (('Status', 'Version'), ('Version', 'Updated At'))
    property_occurrence_cardinality = 1
    value_cardinality = 0
    value_format = object
```
