---
atom_family: SPEC
atom_id: AN-S-3178
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.495131+00:00'
---

## Summary

Declare Ticket Concern

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.Concern

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
    property_occurrence_cardinality = Cardinality(minimum=0, maximum=1)
    value_cardinality = Cardinality(minimum=1, maximum=None)
    value_format = list[dict[str, str]]
```
