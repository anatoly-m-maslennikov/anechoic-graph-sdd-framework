---
atom_family: SPEC
atom_id: AN-S-2598
concern:
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket//.Header.Context
  relation: .
  subject: Template := work_report
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 7
  updated_at: '2026-11-26T17:13:20.415810+00:00'
---
## Summary

Declare Work Report

## Semantics

A Work Report records the changes, checks, results, and remaining gaps from executing its reported Task.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import TicketAtom

class WorkReport(TicketAtom):
    node.template = value(fixed='work_report')
```
