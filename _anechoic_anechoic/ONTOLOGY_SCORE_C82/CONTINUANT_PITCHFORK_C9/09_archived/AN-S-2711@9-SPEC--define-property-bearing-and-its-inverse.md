---
atom_family: SPEC
atom_id: AN-S-2711
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 9
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define Property bearing and its inverse

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_PROPERTY_OF

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_PROPERTY_OF",
    source_endpoint={"level": "model_entities"},
    target_endpoint={"level": "model_entities"},
)
```
