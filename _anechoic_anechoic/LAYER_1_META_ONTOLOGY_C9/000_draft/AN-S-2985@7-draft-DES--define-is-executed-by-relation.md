---
atom_family: SPEC
atom_id: AN-S-2985
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T08:57:34.687078+00:00'
---
## Summary

Define IS_EXECUTED_BY Relation

## Claim

### Formal Claim

```python
# model
relation(source="Relation//IS_EXECUTED_BY", name="HAS_INVERSE", target="Relation//EXECUTES", reverse=True)
```
