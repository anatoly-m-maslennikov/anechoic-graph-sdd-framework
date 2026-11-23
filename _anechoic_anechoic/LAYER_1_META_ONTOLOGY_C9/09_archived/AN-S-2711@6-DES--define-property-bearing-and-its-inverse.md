---
atom_family: SPEC
atom_id: AN-S-2711
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Define Property bearing and its inverse

## Claim

### Prose Claim

IS_PROPERTY_OF directs a Property to exactly one immediate bearer. HAS_PROPERTY is its derived inverse. The bearer relation is acyclic. `Bearer.Property` addresses the Property.

A Property has exactly one immediate bearer; the bearer may be any applicable declared model Entity or instance.

Forward `Host ((IS_PROPERTY_OF)) Target` and reverse `Target <((IS_PROPERTY_OF)) Host` are views of the same Relation fact.
In `X.Y`, Y IS_PROPERTY_OF X; traversal runs from bearer to Property.
IS_PROPERTY_OF relates Property to immediate bearer.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_PROPERTY_OF',
    source_endpoint={'level': 'model_entities_or_instances', 'dependency': 'property'},
    target_endpoint={'level': 'model_entities_or_instances'},
    inverse_alias='HAS_PROPERTY',
    written_alias='.',
    targets_per_source=1,
    acyclic=True,
)
```

