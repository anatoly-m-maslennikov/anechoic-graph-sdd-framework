---
atom_family: SPEC
atom_id: AN-S-2696
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Define RECORDS Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="RECORDS",
    source_endpoint={"level": "instances", "entity_paths": ("Event Record",)},
    target_endpoint={"level": "instances", "entity_paths": ("Event",)},
    inverse_alias="IS_RECORDED_BY",
)
```

## Semantics

RECORDS is the stored Relation from an Event Record to the Event it describes. Its declared inverse IS_RECORDED_BY is a derived view; an Event Record is distinct from the Event.
