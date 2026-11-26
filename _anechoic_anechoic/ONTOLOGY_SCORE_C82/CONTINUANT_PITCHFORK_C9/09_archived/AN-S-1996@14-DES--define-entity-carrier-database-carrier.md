---
atom_family: SPEC
atom_id: AN-S-1996
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 14
  updated_at: "2026-11-25T22:43:43.978015+00:00"
---
## Summary

Define Entity/Carrier/Database Carrier

## Claim

### Prose Claim

A Database Carrier represents content in a database.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class Database(Carrier):
    pass

declare_entity(entity_class=Database, entity_name='Database')
```

