---
atom_family: SPEC
atom_id: AN-S-3609
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: '2026-11-13T06:26:07.833706+00:00'
---
## Summary

Define Plan blocking

## Claim

### Formal Claim

```python
# model
relation(source='Relation//BLOCKS', name='HAS_INVERSE', target='Relation//IS_BLOCKED_BY', reverse=True)
classify(address='Relation//BLOCKS', axis='Derivation', value='Derived', notation='relation')
# instances
relation(source='Atom/(.Header.Context.Role: Plan)//$prerequisite', name='BLOCKS', target='Atom/(.Header.Context.Role: Plan)//$dependent')
```

## Semantics

BLOCKS relates a prerequisite Plan to a dependent Plan that may start only after that prerequisite is Done.
