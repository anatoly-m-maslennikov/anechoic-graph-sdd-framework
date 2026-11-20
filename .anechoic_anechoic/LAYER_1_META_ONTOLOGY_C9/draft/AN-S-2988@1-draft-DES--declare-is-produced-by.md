---
identity:
  atom_id: AN-S-2988
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Declare IS_PRODUCED_BY

## Claim

### Formal Claim

```python
# model
relation(source='Relation//IS_PRODUCED_BY', name='HAS_INVERSE', target='Relation//PRODUCES', reverse=True)
classify(address='Relation//IS_PRODUCED_BY', axis='Derivation', value='Derived', notation='relation')
# instances
relation(source='Event//$event', name='IS_PRODUCED_BY', target='Execution//$execution')
```

## Semantics

IS_PRODUCED_BY links an Event to an Execution that produced it.
