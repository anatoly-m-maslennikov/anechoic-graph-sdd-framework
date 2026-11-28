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
  status: active
  version: 5
  updated_at: "2026-11-28T11:00:50.522707+00:00"
---

## Summary

Declare Ticket Status values

## Semantics

Ticket adds its work and outcome statuses to Current. Standalone
Ticket Assets can use `complete`. A Project can add Current statuses.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, TicketAtom

class TicketAtomStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (TicketAtom,)
    property.value.groups = {
        'backlog': 'Current',
        'in_queue': 'Current',
        'done': 'Current',
        'canceled': 'Current',
        'resolved': 'Current',
        'complete': 'Current',
    }
```
