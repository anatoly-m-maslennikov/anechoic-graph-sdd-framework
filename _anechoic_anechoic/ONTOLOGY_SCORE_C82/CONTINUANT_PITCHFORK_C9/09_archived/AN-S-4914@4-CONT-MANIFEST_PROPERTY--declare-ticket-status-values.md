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
  status: archived
  version: 4
  updated_at: '2026-11-28T09:59:20.838906+00:00'
---

## Summary

Declare Ticket Status values

## Semantics

Ticket Status refines Atom Status with these group memberships.

- Draft contains `draft`.
- Current contains `backlog`, `in_queue`, `canceled`, `done`, and
  `resolved`. It also contains `complete` for standalone Ticket Assets
  and Current Status values admitted by the Project's Model.
- Archived contains `archived`.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, TicketAtom

class TicketAtomStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (TicketAtom,)
    property.value.allowed = (
        'draft', 'backlog', 'in_queue', 'done', 'canceled', 'resolved',
        'complete', 'archived',
    )
    property.value.groups = {
        'draft': 'Draft',
        'backlog': 'Current',
        'in_queue': 'Current',
        'done': 'Current',
        'canceled': 'Current',
        'resolved': 'Current',
        'complete': 'Current',
        'archived': 'Archived',
    }
```
