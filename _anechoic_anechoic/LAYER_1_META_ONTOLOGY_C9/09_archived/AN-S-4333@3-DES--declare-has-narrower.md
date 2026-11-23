---
atom_family: SPEC
atom_id: AN-S-4333
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T05:35:54.631909+00:00'
---
## Summary

Declare HAS_NARROWER

## Claim

### Formal Claim

```python
# model
relation(source="Relation//HAS_NARROWER", name="HAS_INVERSE", target="Relation//NARROWER_THAN", reverse=True)
```
