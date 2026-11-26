---
atom_family: SPEC
atom_id: AN-S-2182
container:
  component: C9
tier: 3
context:
  lens: DES
  template: manifest_property
state:
  status: "archived"
  version: 8
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Declare Atom.Content

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Content

## Formal Manifest

```python anechoic-edsl
from anechoic.model import Atom, Property, Requirement, Method, Evaluation, Delivery
from anechoic.formal_claims import Cardinality

class Content(Property):
    bearer = Atom
    property_occurrence_cardinality = 1
    value_cardinality = 0
    dependent_property_cardinality = Cardinality(minimum=0, maximum=None)
    dependent_property_name_format = str
    recursive_dependent_property_cardinality = Cardinality(minimum=0, maximum=None)
    recursive_dependent_property_name_format = str
    recursive_dependent_property_value_format = "markdown"
    ordered_dependent_property_roles = (Requirement, Method, Evaluation, Delivery)
    ordered_dependent_property_pairs = (("Summary", "Claim"), ("Claim", "Semantics"), ("Semantics", "Details"))
```
