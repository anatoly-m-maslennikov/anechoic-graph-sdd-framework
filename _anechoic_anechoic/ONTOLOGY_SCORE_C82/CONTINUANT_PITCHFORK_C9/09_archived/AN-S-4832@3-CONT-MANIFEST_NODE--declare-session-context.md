---
atom_family: SPEC
atom_id: AN-S-4832
concern:
  subject: Session Context
  path: Model/Graph/Node//Ephemeral
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T18:34:34.815647+00:00"
---

## Summary

Declare Session Context

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Ephemeral

class SessionContext(Ephemeral):
    node.classifications = {'Artifact Kind': 'Ephemeral'}
```
