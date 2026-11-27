---
atom_family: SPEC
atom_id: AN-S-4941
concern:
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket//.Header.Context
  relation: .
  subject: Template := task
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: '2026-11-26T17:13:38.696062+00:00'
---
## Summary

Declare Task

## Semantics

A Task records planned work. An Epic uses this template and has the Epic navigation label.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import TicketAtom

class Task(TicketAtom):
    node.template = value(fixed='task')
```
