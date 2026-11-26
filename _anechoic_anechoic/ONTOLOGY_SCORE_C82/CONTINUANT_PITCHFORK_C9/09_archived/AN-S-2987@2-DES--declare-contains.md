---
atom_family: SPEC
atom_id: AN-S-2987
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Declare CONTAINS

## Claim

### Formal Claim

```python
# model
relation(source='Relation//CONTAINS', name='HAS_INVERSE', target='Relation//IS_CONTAINED_BY', reverse=True)
set_value(address='alias(Relation//CONTAINS)', value='<+')

```
