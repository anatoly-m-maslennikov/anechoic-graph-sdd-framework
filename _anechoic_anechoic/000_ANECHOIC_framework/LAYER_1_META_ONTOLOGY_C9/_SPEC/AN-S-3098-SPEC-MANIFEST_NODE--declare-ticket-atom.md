---
atom_family: SPEC
atom_id: AN-S-3098
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T16:00:37.751377+00:00"
---

## Summary

Declare Ticket Atom

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom

class TicketAtom(Atom):
    node.classifications = {'Temporal Kind': 'Occurrent'}
```
