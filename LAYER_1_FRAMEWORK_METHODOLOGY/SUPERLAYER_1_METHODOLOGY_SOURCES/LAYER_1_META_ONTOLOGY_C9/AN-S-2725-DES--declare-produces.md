---
atom_family: SPEC
atom_id: AN-S-2725
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Declare PRODUCES

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='PRODUCES',
    source_endpoint={"level": "instances", "entity_paths": ('Execution',)},
    target_endpoint={"level": "instances", "entity_paths": ('Event',)},
    inverse_alias='IS_PRODUCED_BY',
)
```

## Semantics

PRODUCES links an Execution to an Event it produced.
