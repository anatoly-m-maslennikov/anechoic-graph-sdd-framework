---
atom_family: SPEC
atom_id: AN-S-3172
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:38.065847+00:00"
---

## Summary

Declare Template

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.Context.Template

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, TicketAtom

class Property3172(Property):
    name = 'Template'
    bearer = Atom.Header.Context
    property.applies_to = (TicketAtom,)
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.format = str
```
