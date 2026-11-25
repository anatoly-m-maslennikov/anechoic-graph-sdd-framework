---
atom_family: SPEC
atom_id: AN-S-2632
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 35
  updated_at: "2026-11-24T23:26:21.245650+00:00"
---
## Summary

Register IS_IMPLEMENTATION_OF relation

## Claim

### Prose Claim

IS_IMPLEMENTATION_OF is the direct Relation owned by a governed Implementation Carrier. The Host is that governed Implementation Carrier and each tuple targets the specification Atom it implements.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_IMPLEMENTATION_OF',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```
