---
atom_family: SPEC
atom_id: AN-S-4332
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T05:35:52.255000+00:00'
---
## Summary

Declare HAS_INSTANCE

## Claim

### Formal Claim

```python
# model
relation(source="Relation//HAS_INSTANCE", name="HAS_INVERSE", target="Relation//INSTANCE_OF", reverse=True)
```
