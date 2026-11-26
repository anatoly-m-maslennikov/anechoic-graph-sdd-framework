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
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.483169+00:00'
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
    applies_to_entity_classes = (TicketAtom,)
    field_options = {'kw_only': True}
    property_occurrence_cardinality = 1
    value_format = str
```
