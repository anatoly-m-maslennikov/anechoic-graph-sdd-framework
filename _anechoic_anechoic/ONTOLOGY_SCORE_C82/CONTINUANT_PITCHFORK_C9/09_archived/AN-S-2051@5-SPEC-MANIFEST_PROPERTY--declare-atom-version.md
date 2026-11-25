---
atom_family: SPEC
atom_id: AN-S-2051
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: '2026-11-24T16:58:01.297434+00:00'
---
## Summary

Declare Atom.Version

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.State.Version

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2051(Property):
    name = 'Version'
    bearer = Atom.Header.State
    minimum_value = 1
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = int
```
