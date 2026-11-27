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
  version: 5
  updated_at: "2026-11-26T15:54:02.456319+00:00"
---

## Summary

Declare Concern

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
    property.dependent_property.name.allowed = ('Subject', 'Path', 'Relation')
    property.dependent_property.ordered_pairs = (('Subject', 'Path'), ('Path', 'Relation'))
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 0
    property.value.format = object
```
