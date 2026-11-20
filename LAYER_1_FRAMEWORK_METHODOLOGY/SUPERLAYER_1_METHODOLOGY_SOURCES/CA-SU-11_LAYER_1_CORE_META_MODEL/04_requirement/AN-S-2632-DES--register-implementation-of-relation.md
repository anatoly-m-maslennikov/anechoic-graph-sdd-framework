---
identity:
  atom_id: AN-S-2632
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 34
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Register implementation_of relation

## Claim

### Prose Claim

implementation_of is the direct Relation owned by a governed Implementation Carrier. The Host is that governed Implementation Carrier and each tuple targets the specification Atom it implements.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='implementation_of',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

