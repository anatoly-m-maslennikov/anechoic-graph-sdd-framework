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
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.343311+00:00'
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
    classifications = {'Temporal Kind': 'Occurrent'}
```
