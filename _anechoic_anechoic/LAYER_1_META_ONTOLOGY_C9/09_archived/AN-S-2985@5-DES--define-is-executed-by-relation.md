---
atom_family: SPEC
atom_id: AN-S-2985
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define IS_EXECUTED_BY Relation

## Claim

### Formal Claim

```python
# model
relation(source="Relation//IS_EXECUTED_BY", name="HAS_INVERSE", target="Relation//EXECUTES", reverse=True)
```
