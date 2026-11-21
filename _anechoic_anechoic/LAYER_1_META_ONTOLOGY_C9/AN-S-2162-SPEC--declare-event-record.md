---
atom_family: SPEC
atom_id: AN-S-2162
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 7
  updated_at: '2026-11-20T14:42:07.157939+00:00'
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

declare_entity(
    entity_name='Event Record',
    entity_class=EventRecord,
    entity_kind='Primary',
)
```
