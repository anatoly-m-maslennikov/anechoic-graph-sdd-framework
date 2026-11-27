---
atom_family: SPEC
atom_id: AN-S-2598
concern:
  subject: Work Report
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-26T17:13:48.993446+00:00"
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
