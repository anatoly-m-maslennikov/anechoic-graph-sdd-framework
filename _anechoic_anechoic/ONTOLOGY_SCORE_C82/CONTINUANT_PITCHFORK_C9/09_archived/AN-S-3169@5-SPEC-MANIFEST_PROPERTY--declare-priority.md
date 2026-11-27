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
  version: 5
  updated_at: "2026-11-26T15:54:02.488381+00:00"
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
