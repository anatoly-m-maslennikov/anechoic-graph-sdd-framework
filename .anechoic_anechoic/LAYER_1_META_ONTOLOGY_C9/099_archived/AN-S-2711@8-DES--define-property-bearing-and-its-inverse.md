---
identity:
  atom_id: AN-S-2711
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 8
  updated_at: '2026-11-14T07:32:51.119753+00:00'
---
## Summary

Define Property bearing and its inverse

## Claim

### Prose Claim

IS_PROPERTY_OF directs a Property to its immediate bearer. HAS_PROPERTY is its derived inverse. `Bearer.Property` addresses the Property.

Forward `Host ((IS_PROPERTY_OF)) Target` and reverse `Target <((IS_PROPERTY_OF)) Host` are views of the same Relation fact.
In `X.Y`, Y IS_PROPERTY_OF X; traversal runs from bearer to Property.
IS_PROPERTY_OF relates Property to immediate bearer.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_PROPERTY_OF',
    endpoint_pairs=(
        {
            'source_endpoint': {'level': 'model_entities', 'dependency': 'property'},
            'target_endpoint': {'level': 'model_entities'},
        },
        {
            'source_endpoint': {'level': 'instances', 'dependency': 'property'},
            'target_endpoint': {'level': 'instances'},
        },
    ),
    inverse_alias='HAS_PROPERTY',
    written_alias='.',
)
```
