---
atom_family: SPEC
atom_id: AN-S-3176
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.558417+00:00"
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
