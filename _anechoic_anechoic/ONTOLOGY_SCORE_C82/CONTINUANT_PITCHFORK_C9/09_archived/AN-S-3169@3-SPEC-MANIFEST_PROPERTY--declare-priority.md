---
atom_family: SPEC
atom_id: AN-S-3169
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.476462+00:00'
---

## Summary

Declare Priority

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.Priority

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, TicketAtom

class Property3169(Property):
    name = 'Priority'
    bearer = TicketAtom.Header
    field_options = {'kw_only': True}
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = int
```
