---
atom_family: SPEC
atom_id: AN-S-3178
concern:
  subject: Concern
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
  version: 4
  updated_at: "2026-11-26T15:52:33.883325+00:00"
---

## Summary

Declare Ticket Concern

## Claim

### Prose Claim

A Ticket Concern is an optional list of locators. Each locator contains Subject, Path, and Relation, as defined in AN-S-3163. For an affected Component, use its ID as `subject`, `Project Structure.components` as `path`, and `affects` as `relation`.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, TicketAtom
from anechoic.formal_claims import Cardinality

class Property3178(Property):
    name = 'Concern'
    bearer = TicketAtom.Header
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = Cardinality(minimum=1, maximum=None)
    property.value.format = list[dict[str, str]]
```
