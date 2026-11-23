---
atom_family: SPEC
atom_id: AN-S-4334
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T05:43:15.642252+00:00'
---
## Summary

Declare IS_SPECIALIZED_BY

## Claim

### Formal Claim

```python
# model
relation(source='Relation//IS_SPECIALIZED_BY', name='HAS_INVERSE', target='Relation//SPECIALIZES', reverse=True)
classify(address='Relation//IS_SPECIALIZED_BY', axis='Derivation', value='Derived', notation='relation')
# instances
relation(source='Atom//$parent', name='IS_SPECIALIZED_BY', target='Atom//$child')
```

## Semantics

IS_SPECIALIZED_BY relates an Atom to an Atom whose Claim specializes its Claim.
