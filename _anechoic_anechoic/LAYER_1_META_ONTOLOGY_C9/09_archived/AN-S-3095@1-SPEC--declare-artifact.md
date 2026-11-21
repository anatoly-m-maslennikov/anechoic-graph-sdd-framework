---
atom_family: SPEC
atom_id: AN-S-3095
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Artifact

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Artifact(Node):
    pass

declare_entity(entity_name="Artifact", entity_class=Artifact)
```
