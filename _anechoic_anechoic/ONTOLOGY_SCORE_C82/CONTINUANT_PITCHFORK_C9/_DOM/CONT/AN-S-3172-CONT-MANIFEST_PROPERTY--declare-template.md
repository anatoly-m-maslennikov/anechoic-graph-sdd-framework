---
atom_family: SPEC
atom_id: AN-S-3172
concern:
  subject: Template
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.Context
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:33.717596+00:00"
---

## Summary

Declare Template

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
