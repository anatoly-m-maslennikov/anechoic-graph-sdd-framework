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
  version: 3
  updated_at: '2026-11-24T16:58:01.492789+00:00'
---

## Summary

Declare the Ticket Atom navigation Label

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket.Header.Context.Label

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
    allowed_values = ('Task', 'Subtask', 'Sub-epic', 'Epic', 'Version')
    field_options = {'default': None, 'kw_only': True}
    value_format = str | None
```
