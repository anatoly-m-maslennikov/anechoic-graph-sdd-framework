---
atom_family: SPEC
atom_id: AN-S-4913
concern:
  subject: Status
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 7
  updated_at: "2026-11-28T11:00:50.522707+00:00"
---

## Summary

Declare Specification Status values

## Semantics

SPEC adds `ready` to Draft and `active` to Current.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, SpecAtom

class SpecAtomStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (SpecAtom,)
    property.value.groups = {
        'ready': 'Draft',
        'active': 'Current',
    }
```
