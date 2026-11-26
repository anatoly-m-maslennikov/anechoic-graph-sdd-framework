---
atom_family: SPEC
atom_id: AN-S-2705
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 10
  updated_at: 2026-11-05 03:46:06 +0400
---
## Summary

Define EXECUTES Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='EXECUTES',
    source_endpoint={"level": "instances", "entity_paths": ('Runtime',)},
    target_endpoint={"level": "instances", "entity_paths": ('Execution',)},
    inverse_alias='IS_EXECUTED_BY',
)
```

## Semantics

EXECUTES is the stored Relation from a Runtime to an Execution. Its declared inverse IS_EXECUTED_BY is a derived view.
