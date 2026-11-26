---
atom_family: SPEC
atom_id: AN-S-2066
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 8
  updated_at: '2026-11-24T16:58:01.299423+00:00'
---

## Summary

Declare Atom.Ref ID

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Ref ID

## Claim

### Prose Claim

Ref ID is computed on read and is not persisted.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2066(Property):
    name = 'Ref ID'
    bearer = Atom
    derived_from_properties = ('Header.Atom ID', 'Header.State.Version', 'Header.State.Status')
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
