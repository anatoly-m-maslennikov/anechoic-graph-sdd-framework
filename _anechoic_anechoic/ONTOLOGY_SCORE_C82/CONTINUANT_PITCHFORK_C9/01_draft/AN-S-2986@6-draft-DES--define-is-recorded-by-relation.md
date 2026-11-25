---
atom_family: SPEC
atom_id: AN-S-2986
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Define IS_RECORDED_BY Relation

## Claim

### Formal Claim

```python
# model
relation(source='Relation//IS_RECORDED_BY', name='HAS_INVERSE', target='Relation//RECORDS', reverse=True)
classify(address='Relation//IS_RECORDED_BY', axis='Derivation', value='Derived', notation='relation')
# instances
relation(source='Event//$event', name='IS_RECORDED_BY', target='Event Record//$record')
```

## Semantics

IS_RECORDED_BY is the derived view from an Event to an Event Record of the stored RECORDS fact.
