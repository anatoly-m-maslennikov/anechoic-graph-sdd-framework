---
atom_family: SPEC
atom_id: AN-S-4914
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:03.493696+00:00"
---

## Summary

Declare Ticket Status values

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.State.Status

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
