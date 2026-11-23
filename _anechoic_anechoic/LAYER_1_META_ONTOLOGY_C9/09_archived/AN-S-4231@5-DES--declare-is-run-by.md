---
atom_family: SPEC
atom_id: AN-S-4231
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: '2026-11-13T06:26:10.910372+00:00'
---
## Summary

Declare IS_RUN_BY

## Claim

### Formal Claim

```python
# model
relation(source='Relation//IS_RUN_BY', name='HAS_INVERSE', target='Relation//RUNS', reverse=True)
```
