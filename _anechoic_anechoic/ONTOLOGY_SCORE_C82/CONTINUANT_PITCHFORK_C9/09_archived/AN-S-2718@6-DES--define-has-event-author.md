---
atom_family: SPEC
atom_id: AN-S-2718
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-26T10:42:57.778129+00:00"
---
## Summary

Define HAS_EVENT_AUTHOR

## Claim

### Prose Claim

HAS_EVENT_AUTHOR identifies the Actor who performed the recorded event.

Forward `Host ((HAS_EVENT_AUTHOR)) Target` and reverse `Target <((HAS_EVENT_AUTHOR)) Host` are views of the same Relation fact.
HAS_EVENT_AUTHOR relates Event Record instance to Actor instance.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='HAS_EVENT_AUTHOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Event Record',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Actor',)},
    inverse_alias='IS_EVENT_AUTHOR_OF',
)
```

