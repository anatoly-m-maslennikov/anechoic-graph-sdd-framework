---
identity:
  atom_id: AN-S-2698
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 9
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define Value Format

## Claim scope

MODEL//ANECHOIC <+ eDSL/Format

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Format:
    pass

declare_entity(entity_name="Format", entity_class=Format)
```
