---
atom_family: SPEC
atom_id: AN-S-3122
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.392969+00:00'
---

## Summary

Declare Family Marker

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, TicketAtom

class Property3122(Property):
    name = 'Family Marker'
    bearer = Atom
    applies_to_entity_classes = (TicketAtom,)
    field_options = {'class_var': True, 'default': 'T'}
    value_format = str
```
