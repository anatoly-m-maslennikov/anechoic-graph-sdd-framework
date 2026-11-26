---
atom_family: SPEC
atom_id: AN-S-3163
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-24T16:58:01.463898+00:00'
---

## Summary

Declare Concern

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Concern

## Claim

### Prose Claim

A Concern locator records a Subject with its Path and Relation. Supply all three together. SPEC and Project Config use one locator. Tickets use an optional list of locators. AN-S-3160 defines the Carrier representation.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3163(Property):
    name = 'Concern'
    bearer = Atom.Header
    allowed_dependent_property_names = ('Subject', 'Path', 'Relation')
    ordered_dependent_property_pairs = (('Subject', 'Path'), ('Path', 'Relation'))
    property_occurrence_cardinality = Cardinality(minimum=0, maximum=1)
    value_cardinality = 0
    value_format = object
```
