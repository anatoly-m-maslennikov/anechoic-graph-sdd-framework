---
atom_family: SPEC
atom_id: AN-S-3169
concern:
  subject: Priority
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:33.615136+00:00"
---

## Summary

Declare Priority

## Semantics

Priority orders Ticket work independently of blocking dependencies and Specification Tier.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, TicketAtom

class Property3169(Property):
    name = 'Priority'
    bearer = TicketAtom.Header
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
