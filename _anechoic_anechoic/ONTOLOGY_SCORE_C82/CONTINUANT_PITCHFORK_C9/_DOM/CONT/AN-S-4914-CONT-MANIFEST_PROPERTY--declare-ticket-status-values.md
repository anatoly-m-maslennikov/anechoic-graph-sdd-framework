---
atom_family: SPEC
atom_id: AN-S-4914
concern:
  subject: Status
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T15:52:36.945546+00:00"
---

## Summary

Declare Ticket Status values

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, TicketAtom

class TicketAtomStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (TicketAtom,)
    property.value.allowed = ('draft', 'backlog', 'in_queue', 'done', 'canceled', 'resolved', 'complete', 'archived')
```
