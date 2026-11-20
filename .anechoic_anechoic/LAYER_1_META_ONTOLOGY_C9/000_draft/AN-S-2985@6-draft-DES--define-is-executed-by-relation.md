---
identity:
  atom_id: AN-S-2985
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Define IS_EXECUTED_BY Relation

## Claim

### Formal Claim

```python
# model
relation(source='Relation//IS_EXECUTED_BY', name='HAS_INVERSE', target='Relation//EXECUTES', reverse=True)
classify(address='Relation//IS_EXECUTED_BY', axis='Derivation', value='Derived', notation='relation')
# instances
relation(source='Execution//$execution', name='IS_EXECUTED_BY', target='Runtime//$runtime')
```

## Semantics

IS_EXECUTED_BY is the derived view from an Execution to a Runtime of the stored EXECUTES fact.
