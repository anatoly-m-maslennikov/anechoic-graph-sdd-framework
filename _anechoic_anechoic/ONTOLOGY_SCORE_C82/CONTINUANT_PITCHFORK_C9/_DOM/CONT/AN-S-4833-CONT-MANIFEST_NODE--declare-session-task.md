---
atom_family: SPEC
atom_id: AN-S-4833
concern:
  subject: Session Task
  path: Model/Graph/Node//Ephemeral
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 6
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare Session Task

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Ephemeral

class SessionTask(Ephemeral):
    pass
```
