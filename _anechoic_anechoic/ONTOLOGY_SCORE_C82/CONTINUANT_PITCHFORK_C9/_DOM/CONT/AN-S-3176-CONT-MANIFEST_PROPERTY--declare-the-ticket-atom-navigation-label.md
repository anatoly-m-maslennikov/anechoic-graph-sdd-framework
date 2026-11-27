---
atom_family: SPEC
atom_id: AN-S-3176
concern:
  subject: Label
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.Context
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:33.853375+00:00"
---

## Summary

Declare the Ticket Atom navigation Label

## Claim

### Meaning

Planning Tickets use the Task Template. The optional Label supports navigation
in Workbench and derived filenames. It does not set containment or lifecycle
rules. Extend the vocabulary here when a new navigation label is needed.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, TicketAtom

class Property3176(Property):
    name = 'Label'
    bearer = TicketAtom.Header.Context
    property.value.allowed = ('Task', 'Subtask', 'Sub-epic', 'Epic', 'Version')
    field_options = {'default': None, 'kw_only': True}
    property.value.format = str | None
```
