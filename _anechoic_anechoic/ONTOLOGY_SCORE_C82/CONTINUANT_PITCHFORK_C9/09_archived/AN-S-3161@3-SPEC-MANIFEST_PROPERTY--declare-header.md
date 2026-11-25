---
atom_family: SPEC
atom_id: AN-S-3161
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.458914+00:00'
---

## Summary

Declare Header

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3161(Property):
    name = 'Header'
    bearer = Atom
    allowed_dependent_property_names = ('Atom Family', 'Atom ID', 'Concern', 'Container', 'Tier', 'Priority', 'Context', 'Relations', 'State')
    ordered_dependent_property_pairs = (('Atom Family', 'Atom ID'), ('Atom ID', 'Concern'), ('Concern', 'Container'), ('Container', 'Tier'), ('Tier', 'Priority'), ('Priority', 'Context'), ('Context', 'Relations'), ('Relations', 'State'))
    property_occurrence_cardinality = 1
    value_cardinality = 0
    value_format = object
```
