---
atom_family: SPEC
atom_id: AN-S-3098
concern:
  subject: Ticket
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 7
  updated_at: '2026-11-26T18:38:58.296902+00:00'
---

## Summary

Declare Ticket Atom

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom

class TicketAtom(Atom):
    node.axes = {'Temporality': 'Occurrent'}
```
