---
atom_family: SPEC
atom_id: AN-S-2162
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 6
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Event Record

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Event Record

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class EventRecord(Artifact):
    pass

declare_entity(entity_name="Event Record", entity_class=EventRecord)
```
