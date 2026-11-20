---
identity:
  atom_id: AN-S-2694
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 13
  updated_at: '2026-11-12T18:19:27.964526+00:00'
---
## Summary

Define is derived relation of relation

## Claim

### Prose Claim

IS_DERIVED_RELATION_OF relates a derived Relation Type instance to its source Relation Type instance. It does not itself specify the endpoint transformation or any qualification. A direct Declaration's inverse binding entails the bound inverse's IS_DERIVED_RELATION_OF link to the direct Relation. A qualified derivation must retain its explicit qualification; it must not be normalized to an unconditional inverse.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_DERIVED_RELATION_OF',
    source_endpoint={'level': 'instances', 'entity_paths': ('Relation',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Relation',)},
)
```

